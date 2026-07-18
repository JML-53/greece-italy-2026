"""Shared helpers for trip photo processing (EXIF/GPS, nearest-stop matching, resizing)."""
import math
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS


def read_exif(path):
    """Return (datetime_str_or_None, lat_or_None, lng_or_None) for a JPEG file."""
    try:
        img = Image.open(path)
        exif = img._getexif()
        if not exif:
            return None, None, None
        tags = {TAGS.get(k, k): v for k, v in exif.items()}
        dt = tags.get('DateTimeOriginal') or tags.get('DateTime')
        gps = tags.get('GPSInfo')
        lat = lng = None
        if gps:
            gtags = {GPSTAGS.get(k, k): v for k, v in gps.items()}
            def conv(coord, ref):
                d, m, s = coord
                val = float(d) + float(m) / 60 + float(s) / 3600
                if ref in ('S', 'W'):
                    val = -val
                return val
            if 'GPSLatitude' in gtags and 'GPSLongitude' in gtags:
                lat = conv(gtags['GPSLatitude'], gtags.get('GPSLatitudeRef', 'N'))
                lng = conv(gtags['GPSLongitude'], gtags.get('GPSLongitudeRef', 'E'))
        return dt, lat, lng
    except Exception:
        return None, None, None


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def nearest_stop(lat, lng, stops, max_km=2):
    best, best_d = None, None
    for s in stops:
        if s.get('lat') is None or s.get('lng') is None:
            continue
        d = haversine_km(lat, lng, s['lat'], s['lng'])
        if best_d is None or d < best_d:
            best, best_d = s, d
    if best and best_d is not None and best_d <= max_km:
        return best, best_d
    return None, None


def resize_jpeg(src_path, dst_path, max_edge, quality=85):
    img = Image.open(src_path)
    img = ImageOps.exif_transpose(img)  # respect camera rotation
    if img.mode != 'RGB':
        img = img.convert('RGB')
    w, h = img.size
    scale = max_edge / max(w, h)
    if scale < 1:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    img.save(dst_path, 'JPEG', quality=quality, optimize=True)
    return dst_path


def upsert_manifest(manifest, record):
    """manifest: list of dicts, mutated in place. Dedup by id."""
    for i, r in enumerate(manifest):
        if r.get('id') == record.get('id'):
            manifest[i] = record
            return manifest
    manifest.append(record)
    return manifest


def write_manifest_js(manifest_list, js_path):
    import json
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('window.PHOTOS = ')
        json.dump(manifest_list, f, ensure_ascii=False, indent=2)
        f.write(';\n')
