"""Render the recording visuals offline. Uses Pillow already in the project env.
Run from any directory: .venv/bin/python docs/diagrams/render_visuals.py
These intentionally simplified visuals accompany the detailed Mermaid sources.
"""
from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parent
W,H=1920,1080
INK='#142C44'; MUTED='#40576D'; BG='#F7F9FC'; LINE='#60788F'
FILL={'local':'#E8F0FA','remote':'#DDF3ED','store':'#FFF0CF','result':'#E9E5F7'}
FONT_DIRS=[Path('/System/Library/Fonts/Supplemental'),Path('/usr/share/fonts/truetype/dejavu')]
def font(size,bold=False):
    for directory in FONT_DIRS:
        for name in (['Arial Bold.ttf','DejaVuSans-Bold.ttf'] if bold else ['Arial.ttf','DejaVuSans.ttf']):
            if (directory/name).exists():return ImageFont.truetype(str(directory/name),size)
    raise RuntimeError('Install/use an Arial or DejaVu Sans font to render visuals.')

class Visual:
    def __init__(self,name,title,subtitle):
        self.name=name;self.im=Image.new('RGB',(W,H),BG);self.d=ImageDraw.Draw(self.im)
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{escape(title)}</title><desc>{escape(subtitle)}</desc><rect width="{W}" height="{H}" fill="{BG}"/>']
        self.text(64,48,title,50,bold=True)
        self.text(64,115,subtitle,26,color=MUTED)
    def text(self,x,y,text,size=28,bold=False,color=INK):
        f=font(size,bold);assert x+self.d.textlength(text,font=f)<W-25,(self.name,text)
        self.d.text((x,y),text,font=f,fill=color,anchor='lt')
        self.parts.append(f'<text x="{x}" y="{y+size*.8}" font-family="Arial, DejaVu Sans, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(text)}</text>')
    def box(self,x,y,w,h,title,lines,kind='local',size=29):
        fill=FILL[kind];self.d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill=fill)
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}"/>')
        title_size=32
        while self.d.textlength(title,font=font(title_size,True))>w-44:title_size-=1
        assert title_size>=24,(self.name,title)
        self.text(x+22,y+20,title,title_size,True)
        for i,line in enumerate(lines):
            actual=size
            while self.d.textlength(line,font=font(actual))>w-44:actual-=1
            assert actual>=22,(self.name,line)
            assert y+66+i*37+actual<y+h,(self.name,line)
            self.text(x+22,y+66+i*37,line,actual)
    def arrow(self,points,label=None,at=None):
        self.d.line(points,fill=LINE,width=4,joint='curve')
        self.parts.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{LINE}" stroke-width="4" stroke-linejoin="round"/>')
        x,y=points[-1];px,py=points[-2];angle=math.atan2(y-py,x-px)
        triangle=[(x,y),(x-15*math.cos(angle-.45),y-15*math.sin(angle-.45)),(x-15*math.cos(angle+.45),y-15*math.sin(angle+.45))]
        self.d.polygon(triangle,fill=LINE)
        self.parts.append('<polygon points="'+' '.join(f'{a:.1f},{b:.1f}' for a,b in triangle)+f'" fill="{LINE}"/>')
        if label:self.text(*at,label,23,color=MUTED)
    def footer(self,text):self.text(64,1010,text,24,color=MUTED)
    def save(self):
        self.parts.append('</svg>');(OUT/f'{self.name}.svg').write_text('\n'.join(self.parts)+'\n')
        self.im.save(OUT/f'{self.name}.png')

v=Visual('system-overview','RunbookIQ | System architecture','Local orchestration and canonical evidence; Pinecone retrieval and Gemini generation')
v.arrow([(300,340),(300,440)],'explicit build / ingest',(335,375))
v.arrow([(530,530),(700,530)],'same chunks',(545,490))
v.arrow([(960,300),(960,380)])
v.arrow([(1220,430),(1300,430),(1300,265),(1390,265)])
v.arrow([(1220,530),(1390,530)])
v.arrow([(960,640),(960,780)])
v.arrow([(530,850),(630,850),(630,600),(700,600)])
v.arrow([(1390,850),(1290,850),(1290,600),(1220,600)])
v.box(70,190,460,150,'Synthetic source documents',['9 Markdown documents','Explicit ingestion path'],'store')
v.box(70,440,460,185,'Canonical local snapshot',['21 retained active chunks','IDs, hashes, versions','BM25 uses this same text'],'store')
v.box(700,190,520,110,'Streamlit / CLI / evaluation',['Question + explicit filters'])
v.box(700,380,520,260,'Compiled LangGraph',['Prepare queries; retrieve + fuse','Select evidence; cache / generate','Validate; optionally repair once','Return current request records'])
v.box(1390,190,460,150,'Gemini Developer API',['Expand, generate, repair','User-confirmed free tier'],'remote')
v.box(1390,440,460,185,'Pinecone services',['Integrated dense embeddings','Dedicated BGE reranker','Returned usage units'],'remote')
v.box(70,780,460,150,'Local SQLite storage',['Query and answer caches','USD 3 ledger + quota counters'],'store')
v.box(700,780,520,150,'Inspectable result',['Cited answer or explicit failure','Sources, stages, usage, timings'],'result')
v.box(1390,780,460,150,'Configuration / private keys',['Phase 2 profile is explicit','Keys stay outside graph state'])
v.footer('Local synthetic assistant. No live incident access or remediation. Nebius is optional Phase 3, inactive.')
v.save()

v=Visual('ingestion-flow','RunbookIQ | Ingestion and publication','A separate explicit command path; ordinary questions never rebuild or re-embed the corpus')
for a,b in [(570,720),(1200,1350)]:v.arrow([(a,330),(b,330)])
v.arrow([(1590,420),(1590,610)])
v.arrow([(1350,700),(1200,700)])
v.arrow([(720,700),(570,700)])
v.box(90,240,480,180,'1  Read and chunk',['Synthetic Markdown sections','Token checks; canonical IDs','Target 400; maximum 2048'])
v.box(720,240,480,180,'2  Candidate snapshot',['Text, metadata, content hashes','Corpus version + manifest','Existing baseline stays frozen'],'store')
v.box(1350,240,480,180,'3  Explicit ingest',['Lock and destination checks','Journal; owned upsert/delete','Pinecone embeds supplied text'],'remote')
v.box(1350,610,480,180,'4  Verify remote freshness',['Fetch expected IDs and hashes','Confirm obsolete IDs removed','Bounded consistency checks'],'remote')
v.box(720,610,480,180,'5  Publish active snapshot',['Atomic local publication','Clear journal only on success','Unchanged corpus skips upsert'],'store')
v.box(90,610,480,180,'6  Ready for questions',['Dense + BM25 share records','Canonical citation evidence','No background refresh'],'result')
v.text(120,885,'Interrupted ingestion keeps the journal: question requests refuse incomplete state.',31,bold=True)
v.footer('The retained experiments use 21 sections-v1 chunks. A future explicit rebuild uses the updated splitter identity.')
v.save()

v=Visual('langgraph-flow','RunbookIQ | The bounded question workflow','Simplified recording view; architecture.md contains every terminal branch and retrieval-only exit')
v.arrow([(330,350),(330,440)])
v.arrow([(330,580),(330,670)])
v.arrow([(570,740),(730,740)])
v.arrow([(970,670),(970,580)],'evidence',(990,615))
v.arrow([(970,440),(970,350)],'fresh response',(995,390))
v.arrow([(1210,245),(1390,245)],'invalid: once',(1225,205))
v.arrow([(1390,315),(1210,315)],'validate again',(1220,350))
v.arrow([(1160,350),(1160,385),(1320,385),(1320,740),(1390,740)])
v.text(1330,450,'valid',23,color=MUTED)
v.arrow([(1210,510),(1320,510)])
v.text(1220,530,'cache',23,color=MUTED)
v.text(1220,560,'hit',23,color=MUTED)
v.arrow([(1210,770),(1390,770)])
v.text(1230,795,'empty',23,color=MUTED)
v.arrow([(1630,350),(1630,670)],'failure',(1660,490))
v.box(90,210,480,140,'1  prepare_request',['Question and explicit filters','Reset request counters'])
v.box(90,440,480,140,'2  prepare_queries',['Original + up to 2 alternatives','Cache or one expansion call'])
v.box(90,670,480,140,'3  retrieve',['Dense + optional BM25 / RRF','Canonical snapshot checks'])
v.box(730,670,480,140,'4  select_evidence',['Optional BGE reranking','At most 5 canonical chunks'])
v.box(730,440,480,140,'5  generate',['Validate cached answer first','Otherwise one answer call'])
v.box(730,210,480,140,'6  validate',['Schema and citation IDs','No semantic entailment test'])
v.box(1390,210,480,140,'7  repair once',['Same question and evidence','Increment before invocation'])
v.box(1390,670,480,180,'END: return result',['Answer, abstention or failure','Current operations and sources','No silent provider fallback'],'result')
v.text(90,910,'Other request, retrieval and provider failures also terminate. Invalid cache entries never trigger repair.',27)
v.footer('State carries data. Nodes return updates. Conditional edges choose the next step. END is not proof of correctness.')
v.save()

v=Visual('retrieval-flow','RunbookIQ | Retrieve, fuse, rerank','Conceptual branches shown side by side; implementation executes query/method searches sequentially')
v.arrow([(430,400),(490,400),(490,300),(550,300)])
v.arrow([(430,440),(490,440),(490,680),(550,680)])
v.arrow([(950,300),(1010,300),(1010,465),(1080,465)])
v.arrow([(950,680),(1010,680),(1010,525),(1080,525)])
v.arrow([(1410,485),(1510,485)])
v.arrow([(1675,580),(1675,780)])
v.box(70,320,360,200,'Query preparation',['Original is retained','0–2 guarded alternatives','At most 3 queries'])
v.box(550,210,400,180,'Pinecone dense search',['Up to 5 hits per query','Semantic similarity','Canonical text checked'],'remote')
v.box(550,590,400,180,'Local BM25',['Up to 5 hits per query','Exact identifiers + terms','Explicit filters before top-k'])
v.box(1080,390,330,190,'RRF fusion',['Ranks, not raw scores','Constant k = 60','Up to 15 candidates'])
v.box(1510,390,330,190,'BGE reranker',['Original question','One bounded call','No silent truncation'],'remote')
v.box(1510,780,330,140,'Selected evidence',['Up to 5 chunks','Canonical citations'],'result')
v.text(80,870,'RRF score = sum of 1 / (60 + original rank)',34,bold=True)
v.text(80,925,'Single-list dense mode preserves order; reranking is independently optional.',27)
v.footer('Relevance scores are not confidence percentages. Good retrieval does not guarantee a supported answer.')
v.save()

v=Visual('cache-and-usage','RunbookIQ | Why zero chat tokens can still mean work','A recorded cache-hit example supplied by the user; no additional API calls were made to create this visual')
rows=[(210,'1  Expansion cache hit',['Reuse original + 2 alternatives'],'store','No Gemini request',['attempted = false; calls = 0']),
      (400,'2  Three dense searches',['Pinecone retrieves evidence again'],'remote','Pinecone consumption',['41 embedding tokens; 3 read units']),
      (590,'3  One reranking request',['Select the most relevant evidence'],'remote','Pinecone consumption',['1 rerank unit']),
      (780,'4  Answer cache hit',['Revalidate cached citations; return answer'],'store','No Gemini request',['New chat usage = 0; prior usage not repeated'])]
for y,title,body,kind,usage,detail in rows:
    v.arrow([(840,y+65),(1060,y+65)])
    if y<780:v.arrow([(470,y+130),(470,y+190)])
    v.box(100,y,740,130,title,body,kind)
    v.box(1060,y,760,130,usage,detail,'result')
v.footer('Chat usage and Pinecone units are separate. Null can mean not applicable or unreported; status supplies the context.')
v.save()
print('Rendered five SVG and five 1920x1080 PNG visuals.')
