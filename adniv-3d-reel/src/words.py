import json,subprocess,numpy as np
d=json.load(open("ref/whisper_words.json")); H=d["hi"]; E=d["en"]
# --- pauses from energy
raw=subprocess.run(["ffmpeg","-v","error","-i","in/vo.mp3","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
a=np.frombuffer(raw,np.float32); hop=160; n=len(a)//hop
db=20*np.log10(np.sqrt((a[:n*hop].reshape(n,hop)**2).mean(1))+1e-6); low=db<-34
pauses=[];i=0
while i<n:
    if low[i]:
        j=i
        while j<n and low[j]: j+=1
        if j-i>=8: pauses.append((i/100,j/100))
        i=j
    else: i+=1
speech_end=float(np.nonzero(~low)[0].max()/100)
P=[
 ["Raat","ki","woh","peeli","roshni...","yaad","hai?"],
 ["Ab","har","gali","mein","safed.","Kab","badla,","aur","kyun?"],
 ["Woh","thi","sodium","lamp.","Uski","roshni","mein","laal,","hara,","neela...","sab","ek","jaisa","dikhta","tha."],
 ["Phir","5","January","2015","ko","shuru","hua","Street","Lighting","National","Programme."],
 ["Ab","tak","ek","crore","chautees","lakh","se","zyada","LED","street","lights","lag","chuki","hain."],
 ["Har","saal","nau","hazaar","million","unit","se","zyada","bijli","bachti","hai..."],
 ["aur","62","lakh","tonne","CO2","kam."],
 ["Par","asli","kamaal","hota","hai","light","ke","andar:","LED","module","aur","driver."],
 ["Yahi","technology","Adniv","banata","hai:","LED","modules,","drivers","aur","complete","lighting","solutions."],
 ["Aapke","sheher","mein","abhi","bhi","peeli","light","hai?","Comment","karke","batao!"],
 ["Adniv...","sahi","roshni,","sahi","partner.","Lighting","consultation","ke","liye","DM","karein,","ya","screen","par","diye","number","par","call","karein."],
]
# overrides: (phrase, word index) -> kind
OV={(3,7):"noasr",(3,8):"noasr",(3,9):"noasr",(3,10):"noasr",
    (4,9):"split_a",(4,10):"split_b",(5,2):"split_a",(5,3):"split_b",(6,4):"merge2",(9,9):"merge2"}
for t_ in H:
    if t_["w"]=="अप": t_["s"]=19.38   # whisper start includes the pause before it
words=[];p=0;pending=[]
def snap_s(t):
    for a_,b_ in pauses:
        if a_-0.02<=t<b_-0.02: return b_
    return t
def snap_e(t):
    for a_,b_ in pauses:
        if a_+0.02<t<=b_+0.02: return a_
    return t
for pi,ph in enumerate(P):
    for wi,w in enumerate(ph):
        k=OV.get((pi,wi))
        if k=="noasr": pending.append((pi,wi,w)); continue
        if k=="split_a": t=H[p]; mid=(t["s"]+t["e"])/2; s,e=t["s"],mid
        elif k=="split_b": t=H[p]; s,e=(t["s"]+t["e"])/2,t["e"]; p+=1
        elif k=="merge2": s,e=H[p]["s"],H[p+1]["e"]; p+=2
        else: s,e=H[p]["s"],H[p]["e"]; p+=1
        if pending:   # distribute unaligned words over the gap before this word
            prev_end=words[-1]["e"] if words else 0
            gs=max(snap_e(prev_end),prev_end); ge=snap_s(s)
            # gap = from end of last aligned word to first pause-end before this token
            lens=[len(x[2].strip('.')) for x in pending]; tot=sum(lens); cur=gs
            # speech window ends at the pause preceding the next phrase
            nxt=[b_ for a_,b_ in pauses if a_>gs and b_<=ge+0.01]
            win_end=[a_ for a_,b_ in pauses if a_>gs+0.3 and b_<=ge+0.01]
            wend=win_end[-1] if win_end else ge
            for (pp,ww,wd),L in zip(pending,lens):
                dur=(wend-gs)*L/tot; words.append(dict(w=wd,ph=pp,s=round(cur,3),e=round(cur+dur,3),src="est")); cur+=dur
            pending=[]
        words.append(dict(w=w,ph=pi,s=round(s,3),e=round(e,3),src="asr"))
for x in words:
    if x["src"]=="asr": x["s"]=round(snap_s(x["s"]),3); x["e"]=round(max(snap_e(x["e"]),x["s"]+0.12),3)
for i in range(len(words)-1):                      # no overlaps
    if words[i]["e"]>words[i+1]["s"]: words[i]["e"]=round(max(words[i+1]["s"]-0.01,words[i]["s"]+0.08),3)
    if words[i]["s"]>=words[i+1]["s"]: words[i+1]["s"]=round(words[i]["s"]+0.09,3)
for x in words:   # "street lights lag" is one fast run inside a 0.36 s window: spread evenly
    if x["ph"]==4 and x["w"]=="street": x["s"],x["e"]=22.69,22.81
    if x["ph"]==4 and x["w"]=="lights": x["s"],x["e"]=22.81,22.93
    if x["ph"]==4 and x["w"]=="lag": x["s"],x["e"]=22.93,23.05
json.dump(dict(words=words,pauses=pauses,speech_end=speech_end,duration=52.193),open("in/words.json","w"),ensure_ascii=False,indent=1)
print(len(words),"words; leftover tokens:",len(H)-p)
for ph in range(len(P)):
    ws=[x for x in words if x["ph"]==ph]
    print(f"P{ph+1} {ws[0]['s']:.2f}-{ws[-1]['e']:.2f}: "+" ".join(f"{x['w']}[{x['s']:.2f}]" for x in ws))
