"""Read existing ASDG image-based PPTX exports without rebuilding the deck."""
import hashlib
import posixpath
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile
from defusedxml import ElementTree as ET

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REFERENCE_MARKER = '\n\n--- Reference metadata (not narration) ---\n'


@dataclass(frozen=True)
class PptxSlide:
    number: int
    folder: Path
    visual: Path
    narration: str
    note_files: tuple
    pptx_parts: dict


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relationships(archive, part):
    directory, name = posixpath.split(part)
    rels = ET.fromstring(archive.read(posixpath.join(directory, '_rels', name + '.rels')))
    result = {}
    for rel in rels:
        if rel.get('TargetMode') == 'External':
            continue
        target = posixpath.normpath(posixpath.join(directory, rel.attrib['Target']))
        if target.startswith('../') or target.startswith('/'):
            raise ValueError('Unsupported PPTX relationship target')
        result[rel.attrib['Id']] = (rel.attrib['Type'].rsplit('/', 1)[-1], target)
    return result


def notes_body(xml):
    root = ET.fromstring(xml)
    bodies = [shape for shape in root.findall('.//p:sp', NS)
              if (ph := shape.find('p:nvSpPr/p:nvPr/p:ph', NS)) is not None
              and ph.get('type') == 'body']
    if len(bodies) != 1:
        raise ValueError('Expected exactly one speaker-notes body')
    paragraphs = []
    for paragraph in bodies[0].findall('p:txBody/a:p', NS):
        pieces = []
        for node in paragraph.iter():
            if node.tag == '{' + NS['a'] + '}t':
                pieces.append(node.text or '')
            elif node.tag == '{' + NS['a'] + '}br':
                pieces.append('\v')  # PowerPoint soft line break
        paragraphs.append(''.join(pieces))
    text = '\n'.join(paragraphs)
    if not text.strip():
        raise ValueError('Empty speaker narration')
    return text


def extract(deck, output, first, last):
    """Only the known single-PNG-on-white ASDG export format is supported."""
    output.mkdir(exist_ok=True)
    result = []
    with ZipFile(deck) as archive:
        presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
        dimensions = presentation.find('p:sldSz', NS)
        width, height = int(dimensions.get('cx')), int(dimensions.get('cy'))
        if abs(width / height - 16 / 9) > 0.001:
            raise ValueError('PPTX experiment requires a 16:9 deck')
        order = presentation.findall('p:sldIdLst/p:sldId', NS)
        if not 1 <= first <= last <= len(order):
            raise ValueError('Slide range is outside the PPTX')
        deck_rels = relationships(archive, 'ppt/presentation.xml')
        for number in range(first, last + 1):
            rel_id = order[number - 1].attrib['{' + NS['r'] + '}id']
            kind, slide_part = deck_rels[rel_id]
            if kind != 'slide':
                raise ValueError('Invalid slide relationship')
            raw = archive.read(slide_part)
            slide = ET.fromstring(raw)
            shapes = slide.findall('p:cSld/p:spTree/*', NS)
            pictures = slide.findall('p:cSld/p:spTree/p:pic', NS)
            if len(pictures) != 1 or any(s.tag.rsplit('}', 1)[-1] not in
                    ('nvGrpSpPr', 'grpSpPr', 'pic') for s in shapes):
                raise ValueError(f'Slide {number}: requires one image and no other visual shapes')
            picture = pictures[0]
            transform = picture.find('p:spPr/a:xfrm', NS)
            offset, extent = transform.find('a:off', NS), transform.find('a:ext', NS)
            if transform.get('rot', '0') != '0' or transform.get('flipH', '0') != '0' or transform.get('flipV', '0') != '0':
                raise ValueError('Rotated/flipped images are unsupported')
            x, y = int(offset.get('x')), int(offset.get('y'))
            cx, cy = int(extent.get('cx')), int(extent.get('cy'))
            if (x < 0 or y < 0 or cx <= 0 or cy <= 0 or x + cx > width + 1 or
                    y + cy > height + 1 or picture.find('p:blipFill/a:srcRect', NS) is not None):
                raise ValueError('PPTX image must fit inside the slide without cropping')
            if slide.find('p:cSld/p:bg', NS) is not None:
                raise ValueError('Explicit PPTX background is unsupported by this white-canvas adapter')
            rels = relationships(archive, slide_part)
            image_id = picture.find('p:blipFill/a:blip', NS).attrib['{' + NS['r'] + '}embed']
            image_kind, image_part = rels[image_id]
            image = archive.read(image_part)
            if image_kind != 'image' or not image.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Only embedded PNG visuals are supported')
            note_parts = [target for kind, target in rels.values() if kind == 'notesSlide']
            if len(note_parts) != 1:
                raise ValueError(f'Slide {number}: missing/ambiguous speaker notes')
            notes_xml = archive.read(note_parts[0])
            notes = notes_body(notes_xml)
            narration, marker, references = notes.partition(REFERENCE_MARKER)
            if not narration.strip():
                raise ValueError('Empty PPTX narration')
            visual = output / f'{number:02d}-pptx-image.png'
            spoken = output / f'{number:02d}-pptx-narration.txt'
            visual.write_bytes(image)
            spoken.write_text(narration, encoding='utf-8')
            (output / f'{number:02d}-pptx-notes-full.txt').write_text(notes, encoding='utf-8')
            result.append(PptxSlide(number, output, visual, narration, (spoken,),
                          {'slide_xml': slide_part, 'slide_xml_sha256': digest(raw),
                           'placement_emu': {'x': x, 'y': y, 'width': cx, 'height': cy,
                                             'slide_width': width, 'slide_height': height},
                           'image': image_part, 'image_sha256': digest(image),
                           'notes_xml': note_parts[0], 'notes_xml_sha256': digest(notes_xml),
                           'notes_body_sha256': digest(notes.encode()),
                           'reference_metadata_excluded': bool(marker),
                           'reference_metadata': references}))
    return result
