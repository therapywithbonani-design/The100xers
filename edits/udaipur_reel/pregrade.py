"""Grade every video frame once (parallel) into graded JPEG sequences.
Usage: python3 pregrade.py <frames_dir> <out_dir>"""
import sys, os, cv2, numpy as np
from multiprocessing import Pool
from grade import grade, measure
SRC, OUT = sys.argv[1:3]
JOBS, LEVELS = [], {}
for n in sorted(os.listdir(SRC)):
    files = sorted(os.listdir(f'{SRC}/{n}'))
    LEVELS[n] = measure([cv2.imread(f'{SRC}/{n}/{f}') for f in files[5::25]])
    os.makedirs(f'{OUT}/{n}', exist_ok=True)
    JOBS += [(n, f) for f in files]
def work(j):
    n, f = j
    g = grade(cv2.imread(f'{SRC}/{n}/{f}'), LEVELS[n])
    cv2.imwrite(f'{OUT}/{n}/{f}', (g * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 96])
if __name__ == '__main__':
    print(LEVELS)
    with Pool(4) as p:
        for k, _ in enumerate(p.imap_unordered(work, JOBS, chunksize=8)):
            if k % 200 == 0: print(k, '/', len(JOBS), flush=True)
