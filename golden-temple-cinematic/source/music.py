import numpy as np, wave, sys
SR=48000; DUR=15.0; N=int(SR*DUR)
t=np.arange(N)/SR
rng=np.random.default_rng(7)
def n2f(m): return 440*2**((m-69)/12)
def env_adsr(n,a,r):
    e=np.ones(n); ai=int(a*SR); ri=int(r*SR)
    e[:ai]=np.linspace(0,1,ai)**2
    e[-ri:]*=np.linspace(1,0,ri)**1.5
    return e
L=np.zeros(N); R=np.zeros(N)
def add(sig,start,pan=0.0,gain=1.0):
    s=int(start*SR); e=min(N,s+len(sig)); sig=sig[:e-s]*gain
    L[s:e]+=sig*np.sqrt(0.5*(1-pan)); R[s:e]+=sig*np.sqrt(0.5*(1+pan))
# chord progression (D major, emotive): Dmaj9, Bm9, Gmaj7#11, Asus4->A
chords=[[50,57,62,66,69,76],[47,54,62,66,69,73],[43,55,59,62,66,73],[45,57,62,64,69,71]]
seg=3.6
for i,ch in enumerate(chords):
    st=0.2+i*seg; ln=seg+2.5
    n=int(ln*SR); tt=np.arange(n)/SR
    for j,m in enumerate(ch):
        f=n2f(m); sig=np.zeros(n)
        for d in (-0.08,0.0,0.07):           # detuned voices
            ff=f*2**(d/12*0.5)
            ph=rng.uniform(0,2*np.pi)
            sig+=np.sin(2*np.pi*ff*tt+ph)+0.28*np.sin(4*np.pi*ff*tt+ph)+0.1*np.sin(6*np.pi*ff*tt)
        sig*=env_adsr(n,1.4,2.4)*(0.9+0.1*np.sin(2*np.pi*0.3*tt+j))
        add(sig,st,pan=(j/len(ch)-0.5)*0.8,gain=0.035 if m>55 else 0.05)
# sub drone
drone=(np.sin(2*np.pi*n2f(38)*t)+0.4*np.sin(2*np.pi*n2f(50)*t))*env_adsr(N,2.5,3.0)
add(drone,0,gain=0.10)
# piano-like plucks melody
mel=[(1.2,74),(2.1,78),(3.0,81),(4.8,78),(5.7,74),(6.6,76),(8.4,79),(9.3,78),(10.2,74),(12.0,73),(12.9,74),(13.5,69)]
for k,(st,m) in enumerate(mel):
    f=n2f(m); n=int(3.5*SR); tt=np.arange(n)/SR
    sig=sum((1/h**1.3)*np.sin(2*np.pi*f*h*tt*(1+0.0004*h))*np.exp(-tt*(1.6+h*0.9)) for h in range(1,7))
    sig*=np.minimum(1,tt/0.004)
    add(sig,st,pan=0.35*np.sin(k),gain=0.11)
# cinematic hit at start + soft swell into final chord
n=int(4*SR); tt=np.arange(n)/SR
boom=np.sin(2*np.pi*(45*np.exp(-tt*0.6))*tt)*np.exp(-tt*1.3)
noise=rng.normal(size=n); noise=np.convolve(noise,np.ones(40)/40,'same')*np.exp(-tt*2.2)
add(boom*0.5+noise*0.15,0.15,gain=0.6)
# shimmer air
air=np.convolve(rng.normal(size=N),np.ones(8)/8,'same')-np.convolve(rng.normal(size=N),np.ones(60)/60,'same')
add(air*env_adsr(N,4,4)*(0.5+0.5*np.sin(2*np.pi*0.12*t)),0,gain=0.012)
# reverb: stereo exponential-noise IR via FFT convolution
def reverb(x,seed):
    r=np.random.default_rng(seed); ln=int(3.2*SR); it=np.arange(ln)/SR
    ir=r.normal(size=ln)*np.exp(-it*2.0); ir=np.convolve(ir,np.ones(6)/6,'same'); ir[:int(0.02*SR)]=0
    M=1<<int(np.ceil(np.log2(len(x)+ln)))
    y=np.fft.irfft(np.fft.rfft(x,M)*np.fft.rfft(ir,M),M)[:len(x)]
    return y/np.max(np.abs(y))*np.max(np.abs(x))
Lw=0.55*L+0.6*reverb(L,1); Rw=0.55*R+0.6*reverb(R,2)
out=np.stack([Lw,Rw],1)
fade=np.ones(N); fo=int(2.5*SR); fade[-fo:]=np.linspace(1,0,fo)**2; fade[:int(0.05*SR)]=np.linspace(0,1,int(0.05*SR))
out*=fade[:,None]
out=np.tanh(out/np.max(np.abs(out))*1.2)*0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out*32767).astype('<i2').tobytes())
