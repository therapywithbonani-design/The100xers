// DOM overlay: depth typography, karaoke captions, chips, logo card, callout labels, CTA. All animation is a pure function of time.
const NAVY='#1B1F54', ORANGE='#F7931E';
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const eo=x=>1-Math.pow(1-x,3), eb=(x,s=1.5)=>{x=x-1;return 1+(s+1)*x*x*x+s*x*x};
const css=`
#hud *{box-sizing:border-box}
.chip{position:absolute;left:64px;top:252px;display:flex;align-items:center;gap:12px;padding:11px 18px;border-radius:999px;
 background:rgba(8,10,30,.55);border:1px solid rgba(255,255,255,.22);backdrop-filter:blur(6px);color:#fff;
 font:500 21px 'JB',monospace;letter-spacing:.09em;text-transform:uppercase;white-space:nowrap}
.chip i{width:11px;height:11px;border-radius:50%;background:${ORANGE};box-shadow:0 0 12px ${ORANGE}}
.logo{position:absolute;right:64px;top:244px;width:292px;height:118px;border-radius:22px;background:#fff;display:flex;align-items:center;justify-content:center;
 box-shadow:0 14px 30px rgba(0,0,0,.45),0 2px 0 rgba(255,255,255,.9) inset}
.logo img{width:256px;height:auto;display:block}
.head{position:absolute;left:64px;width:952px;top:392px;text-align:center;perspective:900px}
.line{display:block;white-space:nowrap;font-family:'ID',sans-serif;font-weight:900;color:#fff;line-height:1.02;letter-spacing:-.02em}
.ch{display:inline-block;transform-origin:50% 100%;will-change:transform}
.em{color:${ORANGE}}
.cap{position:absolute;left:64px;width:876px;top:1372px;text-align:center;font:700 47px/1.26 'IX',sans-serif;letter-spacing:-.005em}
.cap span{display:inline-block;margin:0 .13em;transition:none}
.stat{position:absolute;left:64px;width:952px;top:700px;text-align:center}
.src{position:absolute;left:0;width:1080px;text-align:center;font:500 20px 'JB',monospace;letter-spacing:.1em;color:#fff}
.src b{display:inline-block;padding:9px 16px;border-radius:8px;background:rgba(8,10,30,.6);border:1px solid rgba(247,147,30,.7);font-weight:500}
.lab{position:absolute;display:flex;align-items:center;gap:10px;padding:12px 22px;border-radius:999px;background:rgba(14,16,48,.72);border:2px solid ${ORANGE};
 color:#fff;font:700 28px 'IX',sans-serif;letter-spacing:.06em;text-transform:uppercase;box-shadow:0 0 22px rgba(247,147,30,.45);white-space:nowrap}
.lab i{font-style:normal;color:${ORANGE};font:700 20px 'JB',monospace}
svg.lines{position:absolute;left:0;top:0;width:1080px;height:1920px}
.flash{position:absolute;inset:0;background:#fff;opacity:0}
.fade{position:absolute;inset:0;background:#000;opacity:0}
.cta{position:absolute;left:0;top:0;width:1080px;height:1920px}
.cta .card{position:absolute;left:50%;top:280px;width:560px;height:236px;margin-left:-280px;border-radius:30px;background:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 22px 50px rgba(0,0,0,.5)}
.cta .card img{width:500px}
.cta .h{position:absolute;left:64px;width:952px;top:572px;text-align:center}
.cta .sub{position:absolute;left:64px;width:952px;top:828px;text-align:center;color:#fff;font:600 40px 'IX',sans-serif}
.cta .or{position:absolute;left:64px;width:952px;top:920px;text-align:center;color:rgba(255,255,255,.92);font:500 34px 'IX',sans-serif}
.cta .btn{position:absolute;left:150px;width:780px;height:104px;border-radius:52px;background:${ORANGE};color:#fff;display:flex;align-items:center;justify-content:center;gap:18px;
 font:800 52px 'ID',sans-serif;letter-spacing:.03em;box-shadow:0 18px 36px rgba(0,0,0,.4),0 0 40px rgba(247,147,30,.45),0 3px 0 rgba(255,255,255,.35) inset}
.cta .web{position:absolute;left:64px;width:952px;top:1260px;text-align:center;color:#fff;font:600 44px 'IX',sans-serif;letter-spacing:.02em}
.cta .web u{text-decoration:none;border-bottom:4px solid ${ORANGE};padding-bottom:4px}
`;
function ext(n=9){let s=[];for(let i=1;i<=n;i++){const l=Math.max(8,30-i*2.2);s.push(`${i*.9}px ${i*1.15}px 0 hsl(236 52% ${l}%)`)}
 s.push('0 14px 24px rgba(0,0,0,.55)','0 0 38px rgba(247,147,30,.28)');return s.join(',')}
export function createHUD(root,words){
  const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
  root.innerHTML=`<div class="chip" id="h-chip"><i></i><span></span></div><div class="logo" id="h-logo"><img src="assets/adniv_logo.png"></div>
  <div class="head" id="h-head"></div><div class="stat" id="h-stat"></div><div class="src" id="h-src"></div><div class="cap" id="h-cap"></div>
  <svg class="lines" id="h-lines"></svg><div id="h-labs"></div><div class="cta" id="h-cta" style="display:none"></div><div class="flash" id="h-flash"></div><div class="fade" id="h-fade"></div>`;
  const $=id=>root.querySelector('#'+id);
  const el={chip:$('h-chip'),logo:$('h-logo'),head:$('h-head'),stat:$('h-stat'),src:$('h-src'),cap:$('h-cap'),lines:$('h-lines'),labs:$('h-labs'),cta:$('h-cta'),flash:$('h-flash'),fade:$('h-fade')};
  // caption chunks (<=2 lines)
  const chunks=[];let cur=[];
  words.forEach((w,i)=>{cur.push(i);const n=cur.length,ch=cur.map(k=>words[k].w).join(' ').length;
    if((/[.?!:…]$|\.\.\.$/.test(w.w)&&n>=3)||n>=7||ch>=30||i===words.length-1){chunks.push(cur);cur=[]}});
  const capKey={k:-1};
  function headline(state,t){
    const h=state.head; if(!h){el.head.innerHTML='';return}
    const key=JSON.stringify(h.lines)+h.size; if(el.head._k!==key){el.head._k=key;el.head.style.top=(h.y||392)+'px';el.head.style.fontSize=(h.size||118)+'px';
      el.head.innerHTML=h.lines.map(l=>{let n=0;const parts=l.split('*');
        return '<span class="line">'+parts.map((p,pi)=>[...p].map(c=>{n++;return `<span class="ch ${pi%2?'em':''}" data-n="${n}">${c===' '?'&nbsp;':c}</span>`}).join('')).join('')+'</span>'}).join('')}
    const tt=t-(h.t0||0); let idx=0;
    el.head.querySelectorAll('.line').forEach((ln,li)=>{ln.querySelectorAll('.ch').forEach(c=>{const n=+c.dataset.n;const p=clamp((tt-li*0.14-n*0.032)/0.5);
      const e=eb(p,1.3);c.style.opacity=clamp(p*2.5);c.style.transform=`translateY(${(1-e)*-70}px) rotateX(${(1-e)*-75}deg) scale(${.85+.15*e})`;
      c.style.textShadow=ext(9);})});
    el.head.style.opacity=h.out===undefined?1:h.out;
  }
  function caption(state){
    const c=state.cap; if(!c){el.cap.innerHTML='';capKey.k=-1;return}
    const t=c.t; let ci=-1;
    for(let k=0;k<chunks.length;k++){const a=words[chunks[k][0]].s-0.06;if(t>=a)ci=k}
    if(ci<0){el.cap.innerHTML='';capKey.k=-1;return}
    const last=words[chunks[ci][chunks[ci].length-1]];
    if(t>last.e+0.7&&ci===chunks.length-1&&!c.hold){el.cap.innerHTML='';capKey.k=-1;return}
    if(capKey.k!==ci){capKey.k=ci;el.cap.innerHTML=chunks[ci].map(i=>`<span data-i="${i}">${words[i].w}</span>`).join(' ')}
    let active=-1;chunks[ci].forEach(i=>{if(words[i].s<=t)active=i});
    el.cap.querySelectorAll('span').forEach(s=>{const i=+s.dataset.i;
      if(i===active){s.style.color=ORANGE;s.style.opacity=1;s.style.textShadow=`0 0 20px rgba(247,147,30,.9),0 0 40px rgba(247,147,30,.45),0 3px 6px rgba(0,0,0,.8)`;s.style.transform='scale(1.06)'}
      else if(i<active){s.style.color='#fff';s.style.opacity=1;s.style.textShadow='0 3px 8px rgba(0,0,0,.85)';s.style.transform='none'}
      else{s.style.color='#fff';s.style.opacity=.38;s.style.textShadow='0 3px 8px rgba(0,0,0,.7)';s.style.transform='none'}});
  }
  return {el,apply(state){
    const t=state.t||0;
    el.chip.style.display=state.chip?'flex':'none'; if(state.chip){el.chip.querySelector('span').textContent=state.chip;const p=eo(clamp((t-(state.chipT0||0))/0.5));el.chip.style.opacity=p;el.chip.style.transform=`translateX(${(1-p)*-30}px)`}
    el.logo.style.display=state.logo===false?'none':'flex'; if(state.logo!==false){const p=eo(clamp(t/0.5));el.logo.style.opacity=state.logoOp===undefined?p:state.logoOp}
    headline(state,t); caption(state);
    // source chip
    if(state.src){el.src.style.top=(state.src.y||1300)+'px';el.src.innerHTML=`<b>${state.src.text}</b>`;el.src.style.opacity=state.src.op===undefined?1:state.src.op}else el.src.innerHTML='';
    // labels
    el.lines.innerHTML='';el.labs.innerHTML='';
    (state.labels||[]).forEach((L,i)=>{const p=eo(clamp(L.p===undefined?1:L.p));if(p<=0)return;
      const lx=L.lx,ly=L.ly;
      el.lines.innerHTML+=`<line x1="${L.x}" y1="${L.y}" x2="${L.x+(lx-L.x)*p}" y2="${L.y+(ly-L.y)*p}" stroke="${ORANGE}" stroke-width="3.5" stroke-linecap="round" style="filter:drop-shadow(0 0 6px rgba(247,147,30,.9))"/><circle cx="${L.x}" cy="${L.y}" r="${9*p}" fill="${ORANGE}" stroke="#fff" stroke-width="3"/>`;
      const d=document.createElement('div');d.className='lab';d.style.left=lx+'px';d.style.top=(ly-27)+'px';d.style.opacity=clamp(p*1.6);d.style.transform=`scale(${.85+.15*p})`;d.innerHTML=`<i>${L.n||''}</i>${L.text}`;el.labs.appendChild(d)});
    el.flash.style.opacity=state.flash||0; el.fade.style.opacity=state.fade||0;
    // CTA
    if(state.cta){el.cta.style.display='block';cta(state.cta.t)}else el.cta.style.display='none';
  }};
  function cta(t){
    if(!el.cta._b){el.cta._b=1;el.cta.innerHTML=`<div class="card"><img src="assets/adniv_logo.png"></div><div class="h" id="c-h"></div><div class="sub">DM us to book a lighting consultation</div><div class="or">or call</div>
     <div class="btn" id="c-b1" style="top:1000px">99108 13339</div><div class="btn" id="c-b2" style="top:1126px">93190 74766</div><div class="web"><u>www.adniv.in</u></div>`;
     const lines=['Sahi roshni,','*sahi partner.*'];el.cta.querySelector('#c-h').innerHTML=lines.map(l=>{let n=0;return '<span class="line" style="font-size:112px">'+l.split('*').map((p,pi)=>[...p].map(c=>{n++;return `<span class="ch ${pi%2?'em':''}" data-n="${n}">${c===' '?'&nbsp;':c}</span>`}).join('')).join('')+'</span>'}).join('');}
    const q=s=>el.cta.querySelector(s);
    const card=q('.card'),p0=eo(clamp(t/0.6));card.style.opacity=p0;card.style.transform=`translateY(${(1-p0)*-40}px) scale(${.92+.08*p0})`;
    q('#c-h').querySelectorAll('.line').forEach((ln,li)=>ln.querySelectorAll('.ch').forEach(c=>{const n=+c.dataset.n;const p=clamp((t-0.35-li*0.14-n*0.03)/0.5),e=eb(p,1.3);
      c.style.opacity=clamp(p*2.5);c.style.transform=`translateY(${(1-e)*-70}px) rotateX(${(1-e)*-75}deg)`;c.style.textShadow=ext(9)}));
    const fade=(s,t0,dy=24)=>{const p=eo(clamp((t-t0)/0.5));const e=q(s);e.style.opacity=p;e.style.transform=`translateY(${(1-p)*dy}px)`};
    fade('.sub',1.2);fade('.or',1.55,14);
    ['#c-b1','#c-b2'].forEach((s,i)=>{const p=clamp((t-1.75-i*0.2)/0.5),e=eb(p,1.4),b=q(s);b.style.opacity=clamp(p*2);b.style.transform=`scale(${.7+.3*e})`});
    fade('.web',2.5,14);
  }
}
