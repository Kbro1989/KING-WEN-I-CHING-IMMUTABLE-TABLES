"""Full paper vocabulary extractor for King Wen hexagram domain mapping.

For each paper:
- Extract ALL words, symbols, numbers, phrases
- Count repetitions
- Capture context windows
- Route to top-K hexagrams by per-hex keyword fit, not broad category matches

Output: per-hexagram full vocabulary with context, not just top 6 words.
"""
from pathlib import Path
import json, re, csv
from collections import defaultdict, Counter

TEXT_DIR = Path('C:/Users/krist/Desktop/zotero/learning-corpus/.text')
ROOT = Path(__file__).resolve().parent.parent
ARCHETYPES = ROOT / "output" / "hexagram_coder_archetypes.csv"
OUT = ROOT / "output" / "hexagram_full_vocabulary.json"

archetypes = {}
with ARCHETYPES.open('r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        archetypes[row['hexagram_id']] = row

print(f'archetypes: {len(archetypes)}')

STOP = {
    'the','and','for','with','from','that','this','they','have','been','were','their','would','could','should','which','where','when','what','than','then','them','also','more','most','some','into','over','such','only','other','many','much','each','about','because','through','during','before','after','above','below','between','same','different','often','however','although','while','since','until','because','both','few','most','own','same','than','too','very','just','still','already','ever','never','always','usually','sometimes','really','perhaps','certainly','definitely','probably','possible','likely','clear','known','given','shown','found','used','using','based','proposed','presented','introduced','developed','designed','implemented','evaluated','compared','analyzed','discussed','reported','demonstrated','shown','observed','results','method','approach','model','models','paper','propose','present','introduce','show','result','performance','accuracy','improvement','state','art','using','based','et','al','fig','figure','table','equation','section','appendix','references','abstract','introduction','conclusion','future','work','we','our','can','may','will','not','are','was','were','been','being','has','had','does','did','say','said','could','would','should','might','must','shall','this','that','these','those','there','here','where','when','how','what','why','who','whom','whose','which','while','although','because','since','until','before','after','during','about','against','between','through','within','without','under','over','above','below','upon','between','among','throughout','despite','toward','towards','upon','regarding','concerning','including','plus','minus','times','divided','equals','equal','less','greater','than','less','greater','equal','one','two','three','four','five','six','seven','eight','nine','zero','first','second','third','fourth','fifth','last','next','previous','new','old','large','small','high','low','long','short','good','bad','best','worst','better','worse','much','many','few','several','some','any','all','every','each','both','either','neither','other','another','same','different','such','no','yes','true','false','right','wrong','correct','incorrect','possible','impossible','necessary','sufficient','important','significant','relevant','irrelevant','related','unrelated','similar','different','common','rare','frequent','infrequent','typical','atypical','normal','abnormal','standard','nonstandard','expected','unexpected','known','unknown','given','fixed','variable','constant','changing','static','dynamic','stable','unstable','simple','complex','easy','difficult','hard','soft','fast','slow','early','late','recent','ancient','modern','traditional','contemporary','classic','novel','current','future','past','present','ongoing','continuous','discrete','finite','infinite','single','multiple','double','triple','quadruple','single','double','triple','quadruple','first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth','sixteenth','seventeenth','eighteenth','nineteenth','twentieth','thirtieth','hundred','thousand','million','billion','trillion','b','kb','mb','gb','tb','pb','hz','khz','mhz','ghz','thz','ns','us','ms','s','min','hr','day','week','month','year','century','millennium','percent','%','degree','°','radian','steradian','meter','m','kilometer','km','cm','mm','um','nm','pm','fm','gram','g','kg','mg','ug','ng','liter','l','ml','ul','mole','mol','mmol','umol','nmol','pascal','pa','kpa','mpa','gpa','bar','atm','torr','psi','joule','j','kj','cal','kcal','watt','w','kw','mw','horsepower','hp','volt','v','mv','kv','amp','a','ma','ka','ohm','ω','kohm','mohm','farad','f','uf','nf','pf','henry','h','mh','uh','tesla','t','gt','gauss','celsius','c','fahrenheit','f','kelvin','k','lux','lm','cd','candela','lumen','becquerel','bq','kbq','mbq','gbq','gray','gy','kgy','mgy','sievert','sv','msv','usv','kat','katal','mol/s',
    'arxiv','abs','doi','https','http','org','com','edu','pdf','html','xml','json','csv','tsv','txt','md','yml','yaml','toml','ini','cfg','conf','sh','bash','zsh','fish','py','js','ts','jsx','tsx','css','scss','less','html','java','cpp','c','h','rs','go','rb','php','swift','kt','scala','r','m','mat','ipynb','sql','graphql','proto','cap','md5','sha','base64','zip','tar','gz','bz2','xz','dmg','exe','so','dll','lib','a','o','obj','class','jar','war','egg','whl','deb','rpm','apk','ipa','appx','msi','cab','iso','img','vhd','vhdx','qcow2','raw','bin','hex','srec','mot','elf','pe','mach-o','wasm','bc','ll','bc','mir','air','apk','ipa','xap','appx','appxbundle','msix','msixbundle','appxupload','appxmanifest','appxrecipe','appxsym','appxupload','appxbundle','appxmanifest','appxrecipe','appxsym',
    'github','gitlab','bitbucket','git','svn','hg','bzr','cvs','npm','yarn','pnpm','pip','conda','mamba','poetry','cargo','go','cargo','stack','cabal','mix','rebar','lein','sbt','mvn','gradle','ant','make','cmake','ninja','meson','bazel','buck','pants','please','shard','dub','vcpkg','conan','vcpkg','portage','apt','yum','dnf','brew','choco','scoop','winget',' Chocolatey','Scoop','winget','apt-get','yum','dnf','pacman','zypper','emerge','pkg','apk','opkg','pipx','pipenv','virtualenv','venv','conda','mamba',' micromamba','asdf','fnm','nvm','pyenv','rbenv','nodenv','goenv','jenv','phpenv','perlbrew','plenv','swiftenv','hsenv','cargo','rustup','gvm','sdkman','jabba','antigen','antibody','basher','batz','dotfiles','oh-my-zsh','prezto','zinit','zgen','zplug','zap','starship','powerlevel10k','p10k','oh-my-posh','clink','psreadline','psake','cake','fake','invoke','fabric','pyinvoke','ansible','salt','puppet','chef','terraform','cloudformation','cdk','pulumi','crossplane','terragrunt','atlantis','driftctl','checkov','tfsec','sops','vault','boundary','consul','nomad','waypoint','nomad','fabio','traefik','envoy','istio','linkerd','kuma','osm','cilium','calico','flannel','weave','kube-router','romana','cilium','calico','flannel','weave','kube-router','romana','cilium','calico','flannel','weave','kube-router','romana',
}

HEX_KEYWORDS = {
    '1': ['research','novel architecture','benchmark','state-of-the-art','sota','propose','introduce','method','approach','generalization','scalable','training dynamics','large language model','vision language model','language model','foundation model','multimodal','agent','reasoning','transformer','diffusion','generative','robot','embodied','game','neural','deep','learning','representation','dataset','benchmark','evaluation','state-of-the-art'],
    '2': ['verification','validation','audit','check','verify','validate','assess','evaluate','benchmark','compare','analyze','review','inspect','test','examination','skepticism','doubt','challenge','question','reproducibility','replicate','ground truth','gold standard','manual','inspection','robustness','generalization','out-of-distribution','ood','calibration','confidence','uncertainty','ablation','failure','error case','baseline','statistical','significance','trust','safe','safety','risk','compliance','policy','guard','threshold','limit','boundary','constraint'],
    '3': ['initialization','initialize','pretrain','cold start','bootstrap','startup','launch','begin','start','init','from scratch','scratch','random','seed','warm start','cold-start','initial','born','creation','inception','genesis','origin','first','early','toy','minimal','simple','ablation study','baseline'],
    '4': ['survey','review','overview','introduction','tutorial','beginner','guide','learn','teach','explain','primer','walkthrough','course','curriculum','education','mentor','coach','instructor','student','classroom','lesson','chapter','appendix','background','history','taxonomy','categorization','landscape','state-of-the-art','sota','comprehensive','broad','shallow','introductory'],
    '5': ['queue','scheduling','priority','delay','latency','buffer','waiting','timeout','wait','queueing','arrival','service','departure','throughput','rate','throttle','backoff','retry','exponential','jitter','deadline','real-time','temporal','timing','rhythm','cadence','pacing','intermittent','sporadic','bursty'],
    '6': ['analytics','evaluation','metric','benchmark','comparison','ablation','statistical','significance','confidence','error analysis','failure case','baseline','accuracy','loss','score','performance','precision','recall','auc','calibration','out-of-distribution','ood','uncertainty','robustness','fairness','bias','variance','noise'],
    '7': ['blueprint','system design','architecture','pipeline','workflow','orchestrat','interface','protocol','integration','modular','deployment','specification','api','service','scheduler','control flow','router','registry','dispatch','policy','access control','auth','middleware','gateway'],
    '8': ['consensus','agreement','coordination','alignment','cooperation','harmony','multi-party','multi-stakeholder','federation','convergence','joint','shared','collective','team','swarm','society','community','collaboration','negotiation','contract','treaty','protocol','handshake','mutual','reciprocal','symmetry','balance','equilibrium'],
    '9': ['red team','adversarial','security','jailbreak','robustness','backdoor','poison','defense','watermark','audit','vulnerability','attack','evasion','prompt injection','extraction','membership inference','trojan','escape','bypass','safety','refusal','harmful','toxicity'],
    '10': ['database','storage','persistence','index','retrieval','query','schema','migration','transaction','consistency','replication','cache','key-value','vector database','embedding store','memory','checkpoint','state','snapshot','replay','persist','serialization','object store','blob','filesystem','disk','ssd','hdd'],
    '11': ['async','networking','distributed','communication','message passing','rpc','api','service mesh','load balance','latency','throughput','protocol','tcp','http','websocket','grpc','queue','stream','bandwidth','packet','socket','endpoint','node','cluster','fault','partition','replica','shard','consensus','raft','paxos'],
    '12': ['ci/cd','devops','pipeline','deployment','release','rollback','monitor','alert','incident','postmortem','slo','sli','error budget','build','artifact','test','lint','deploy','rollback','canary','blue green','infrastructure','terraform','kubernetes','docker','container','image'],
    '13': ['collaboration','multi-agent','team','society','coordination','consensus','negotiation','communication protocol','role assignment','swarm','shared memory','handoff','delegation','tool use','agent','workflow','planning','execution','feedback','joint','partition','split','merge','negotiation'],
    '14': ['dev','implementation','engineering','production','refactor','technical debt','codebase','tooling','debug','profiling','observability','provenance','lineage','catalog','dataset','harvest','metadata','repository','record','ownership','audit','traceability'],

        'word_contexts': {w: ctxs[:3] for w, ctxs in word_contexts.items()},
        'symbols': dict(symbol_counts.most_common(50)),
        'numbers': dict(number_counts.most_common(30)),
        'bigrams': dict(bigram_counts.most_common(50)),
        'trigrams': dict(trigram_counts.most_common(30)),
        'latex': dict(latex_counts.most_common(30)),
        'total_words': len(words),
        'unique_words': len(word_counts),
        'total_symbols': len(symbols),
        'unique_symbols': len(symbol_counts),
    }


def route_paper_to_hexagrams(paper_id, text):
    tokens = _tokenize(text)
    scores = Counter()
    for hid, keywords in HEX_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if _keyword_token_hits(kw, tokens):
                score += 1
        if score:
            scores[hid] = score
    top = [hid for hid, _ in scores.most_common(5)]
    if not top:
        top = ['1']
    return set(top)

# Main
files = sorted(TEXT_DIR.glob('*.txt'))
print(f'processing {len(files)} papers...')

hex_vocab = defaultdict(lambda: {
    'words': Counter(),
    'symbols': Counter(),
    'numbers': Counter(),
    'bigrams': Counter(),
    'trigrams': Counter(),
    'latex': Counter(),
    'papers': [],
    'contexts': defaultdict(list),
    'paper_ids': [],
})

processed = 0
for path in files:
    paper_id = path.stem.split('_', 1)[1] if '_' in path.stem else path.stem
    txt = path.read_text(encoding='utf-8', errors='ignore')
    if len(txt.strip()) < 200:
        continue
    processed += 1
    vocab = extract_full_vocabulary(txt, paper_id)
    matched_hids = route_paper_to_hexagrams(paper_id, txt)

    for hid in matched_hids:
        hv = hex_vocab[hid]
        if paper_id not in hv['paper_ids']:
            hv['papers'].append(paper_id)
            hv['paper_ids'].append(paper_id)

        for w, c in vocab['words'].items():
            if len(w) > 2 and w not in STOP:
                hv['words'][w] += c
                if w in vocab['contexts']:
                    hv['contexts'][w].extend(vocab['contexts'][w][:2])

        for s, c in vocab['symbols'].items():
            hv['symbols'][s] += c
        for n, c in vocab['numbers'].items():
            hv['numbers'][n] += c
        for bg, c in vocab['bigrams'].items():
            hv['bigrams'][bg] += c
        for tg, c in vocab['trigrams'].items():
            hv['trigrams'][tg] += c
        for lp, c in vocab['latex'].items():
            hv['latex'][lp] += c

print(f'papers processed: {processed}')
print(f'hexagrams with vocab: {len(hex_vocab)}')

# Distinctiveness: compute global word frequencies across all hexes
global_word_counts = Counter()
for hv in hex_vocab.values():
    global_word_counts.update(hv['words'])

output = {}
for hid in sorted(archetypes.keys(), key=int):
    hv = hex_vocab.get(hid)
    arch = archetypes.get(hid, {})
    if hv is None:
        output[hid] = {
            'hexagram_id': int(hid),
            'name': arch.get('name', ''),
            'category': arch.get('category', ''),
            'action': arch.get('action', ''),
            'coder_role': f"{arch.get('category', '')} {arch.get('action', '')} — {arch.get('archetype', '')}",
            'vocabulary': {
                'top_words': [], 'distinctive_words': [], 'top_symbols': [], 'top_numbers': [], 'top_bigrams': [], 'top_trigrams': [], 'latex_commands': [], 'total_unique_words': 0, 'total_papers': 0, 'paper_ids': []
            },
        }
        continue

    top_words = []
    for word, count in hv['words'].most_common(100):
        contexts = hv['contexts'].get(word, [])[:3]
        top_words.append({
            'word': word,
            'count': count,
            'contexts': contexts,
            'usage': f"appears {count} times across {len(hv['papers'])} papers",
        })

    distinctive = []
    for word, count in hv['words'].most_common(300):
        global_count = global_word_counts.get(word, 0)
        distinctiveness = count / (global_count + 1)
        if distinctiveness >= 0.05 and count >= 2:
            contexts = hv['contexts'].get(word, [])[:2]
            distinctive.append({
                'word': word,
                'hex_count': count,
                'global_count': global_count,
                'distinctiveness': round(distinctiveness, 3),
                'contexts': contexts,
            })
    distinctive.sort(key=lambda x: x['distinctiveness'], reverse=True)
    distinctive = distinctive[:120]

    output[hid] = {
        'hexagram_id': int(hid),
        'name': arch.get('name', ''),
        'category': arch.get('category', ''),
        'action': arch.get('action', ''),
        'coder_role': f"{arch.get('category', '')} {arch.get('action', '')} — {arch.get('archetype', '')}",
        'vocabulary': {
            'top_words': top_words,
            'distinctive_words': distinctive,
            'top_symbols': [{'symbol': s, 'count': c} for s, c in hv['symbols'].most_common(30)],
            'top_numbers': [{'number': n, 'count': c} for n, c in hv['numbers'].most_common(20)],
            'top_bigrams': [{'phrase': bg, 'count': c} for bg, c in hv['bigrams'].most_common(20)],
            'top_trigrams': [{'phrase': tg, 'count': c} for tg, c in hv['trigrams'].most_common(15)],
            'latex_commands': [{'cmd': lp, 'count': c} for lp, c in hv['latex'].most_common(20)],
            'total_unique_words': len(hv['words']),
            'total_papers': len(hv['papers']),
            'paper_ids': hv['paper_ids'][:20],
        },
    }

with OUT.open('w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f'wrote {OUT}')
print(f'size MB: {OUT.stat().st_size / 1024 / 1024:.2f}')

for hid in ['1', '6', '9', '29', '64']:
    hd = output.get(hid, {})
    print(f"\n{hid}: {hd.get('name')} — {hd.get('coder_role')}")
    print(f"  unique_words: {hd.get('vocabulary', {}).get('total_unique_words')}")
    print(f"  papers: {hd.get('vocabulary', {}).get('total_papers')}")
    print(f"  top 8 words: {[w['word'] for w in hd.get('vocabulary', {}).get('top_words', [])[:8]]}")
    print(f"  top symbols: {[s['symbol'] for s in hd.get('vocabulary', {}).get('top_symbols', [])[:5]]}")
    print(f"  top bigrams: {[b['phrase'] for b in hd.get('vocabulary', {}).get('top_bigrams', [])[:3]]}")
    print(f"  latex cmds: {[l['cmd'] for l in hd.get('vocabulary', {}).get('latex_commands', [])[:3]]}")
