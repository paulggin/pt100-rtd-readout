import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R0,A,B=100.0,3.9083e-3,-5.775e-7
def T_of_R(R):
    a,b,c=B,A,1-R/R0; return (-b+np.sqrt(b*b-4*a*c))/(2*a)
d=np.genfromtxt("spice/vout_sweep_4wire.csv")
R=d[:,0]; V=d[:,1]          # positive output now
Ttrue=T_of_R(R)
m,b=np.polyfit(R,V,1); fit=m*R+b
R2=1-np.sum((V-fit)**2)/np.sum((V-np.mean(V))**2)
mc=(V[-1]-V[0])/(R[-1]-R[0]); bc=V[0]-mc*R[0]
Rrec=(V-bc)/mc; res=T_of_R(Rrec)-Ttrue
LSB=3.3/4096; Vq=np.round(V/LSB)*LSB; resq=T_of_R((Vq-bc)/mc)-Ttrue
print(f"Vout: {V[0]*1e3:.1f} mV -> {V[-1]*1e3:.0f} mV   span {(V[-1]-V[0]):.3f} V  ({(V[-1]-V[0])/100*1e3:.1f} mV/C)")
print(f"linearity R^2 = {R2:.8f}")
print(f"recovery (ideal): {np.max(np.abs(res))*1e3:.2e} mC ;  (12-bit ADC): {np.max(np.abs(resq)):.3f} C")
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
ax[0].plot(Ttrue,V,color="#0F6E56",lw=2)
ax[0].set_xlabel("true temperature (°C)"); ax[0].set_ylabel("readout V(Vout) (V)")
ax[0].set_title("SPICE sweep — readout output vs temperature"); ax[0].grid(alpha=.3)
ax[0].annotate(f"R² = {R2:.6f}\n{(V[-1]-V[0])/100*1e3:.1f} mV/°C",xy=(.05,.82),xycoords="axes fraction",fontsize=9,color="#333")
ax[1].plot(Ttrue,resq*1e3,color="#2B4BA0",lw=1.4,label="12-bit ADC (3.3 V)")
ax[1].axhline(0,color="#0F6E56",lw=1,ls="--",label="ideal analog chain")
ax[1].set_xlabel("true temperature (°C)"); ax[1].set_ylabel("recovered − true (m°C)")
ax[1].set_title("Temperature recovery via inverse Callendar–Van Dusen"); ax[1].grid(alpha=.3); ax[1].legend(fontsize=9)
fig.tight_layout(); fig.savefig("plots/recovery_result.png",dpi=140); print("saved")
