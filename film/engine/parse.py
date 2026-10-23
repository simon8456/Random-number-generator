"""Parser scénáře (scenar.txt) do seznamu scén a příkazů."""
import re
import shlex

LINE_RE = re.compile(r'^([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ_]+)\s*(\((vo)\))?\s*(\[(\w+)\])?\s*:\s*(.+)$')


class Scene:
    def __init__(self, sid, set_name, tod):
        self.id = sid
        self.set = set_name
        self.tod = tod
        self.cmds = []

    def __repr__(self):
        return f"Scene({self.id},{self.set},{self.tod},{len(self.cmds)} cmds)"


def parse(path):
    scenes = []
    cur = None
    with open(path, encoding='utf8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('# '):
                continue
            if line.startswith('## '):
                parts = line[3:].split()
                cur = Scene(parts[0], parts[1], parts[2] if len(parts) > 2 else 'day')
                scenes.append(cur)
                continue
            if cur is None:
                continue
            if line.startswith('@'):
                toks = shlex.split(line[1:])
                cur.cmds.append(('cmd', toks[0], toks[1:]))
                continue
            m = LINE_RE.match(line)
            if not m:
                raise ValueError(f"Nerozumím řádku: {line}")
            who, vo, mood, text = m.group(1), bool(m.group(3)), m.group(5), m.group(6).strip()
            cur.cmds.append(('line', who, {'vo': vo, 'mood': mood, 'text': text}))
    return scenes


def all_lines(scenes):
    for sc in scenes:
        for c in sc.cmds:
            if c[0] == 'line':
                yield sc, c


if __name__ == '__main__':
    import sys, collections
    scs = parse(sys.argv[1])
    cnt = collections.Counter()
    words = 0
    for sc, c in all_lines(scs):
        cnt[c[1]] += 1
        words += len(c[2]['text'].split())
    print(len(scs), 'scén', sum(cnt.values()), 'replik', words, 'slov')
    print(cnt.most_common())
    seqs = sorted({a[0] for sc in scs for k, n, a in sc.cmds if k == 'cmd' and n == 'seq'})
    print(len(seqs), 'sekvencí:', seqs)
    sfx = sorted({a[0] for sc in scs for k, n, a in sc.cmds if k == 'cmd' and n == 'sfx'})
    print('sfx:', sfx)
    mus = sorted({a[0] for sc in scs for k, n, a in sc.cmds if k == 'cmd' and n == 'music'})
    print('music:', mus)
    amb = sorted({a[0] for sc in scs for k, n, a in sc.cmds if k == 'cmd' and n == 'amb'})
    print('amb:', amb)
    sets = sorted({sc.set for sc in scs})
    print('sets:', sets)
    waits = sum(float(a[0]) for sc in scs for k, n, a in sc.cmds if k == 'cmd' and n == 'wait')
    print('wait s:', waits)
