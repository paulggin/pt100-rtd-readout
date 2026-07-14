import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R0,A,B=100.0,3.9083e-3,-5.775e-7
def T_of_R(R):
    a,b,c=B,A,1-R/R0; return (-b+np.sqrt(b*b-4*a*c))/(2*a)
U="spice/"
d4=np.genfromtxt(U+"vout_sweep_4wire.csv")   # 4-wire SPICE sweep
d2=np.genfromtxt(U+"vout_sweep_2wire.csv")   # 2-wire SPICE sweep (R5 = 2 ohm in the sensed loop)
R=d4[:,0]; V4=d4[:,1]; V2=d2[:,1]
Ttrue=T_of_R(R)
# calibrate on the 4-wire sweep, apply the SAME calibration to both
mc=(V4[-1]-V4[0])/(R[-1]-R[0]); bc=V4[0]-mc*R[0]
def recoverT(V): return T_of_R((V-bc)/mc)
T4=recoverT(V4); T2=recoverT(V2)
e4=T4-Ttrue; e2=T2-Ttrue
print(f"4-wire: Vout {V4[0]*1e3:.1f}->{V4[-1]*1e3:.0f} mV ; apparent error {np.mean(e4)*1e3:+.2f} mC")
print(f"2-wire: Vout {V2[0]*1e3:.1f}->{V2[-1]*1e3:.0f} mV ; apparent error {e2[0]:+.2f}..{e2[-1]:+.2f} C (mean {np.mean(e2):+.2f})")

fig,ax=plt.subplots(1,2,figsize=(11,4.2))
ax[0].plot(Ttrue,T2,color="#B23A48",lw=2,label="2-wire (SPICE)")
ax[0].plot(Ttrue,T4,color="#0F6E56",lw=2,label="4-wire (SPICE)")
ax[0].plot(Ttrue,Ttrue,color="#888",lw=1,ls=":",label="true")
ax[0].set_xlabel("true temperature (°C)"); ax[0].set_ylabel("recovered temperature (°C)")
ax[0].set_title("Recovered temperature — 2-wire vs 4-wire"); ax[0].grid(alpha=.3); ax[0].legend(fontsize=9)
ax[1].plot(Ttrue,e2,color="#B23A48",lw=2,label="2-wire")
ax[1].plot(Ttrue,e4,color="#0F6E56",lw=2,label="4-wire")
ax[1].axhline(0,color="#888",lw=1,ls=":")
ax[1].set_xlabel("true temperature (°C)"); ax[1].set_ylabel("apparent error (°C)")
ax[1].set_title("Lead-resistance error (R_lead = 2 Ω, from SPICE)"); ax[1].grid(alpha=.3); ax[1].legend(fontsize=9)
ax[1].annotate(f"+{np.mean(e2):.1f} °C\ncancelled by 4-wire",xy=(.32,.5),xycoords="axes fraction",fontsize=10,color="#B23A48")
fig.tight_layout(); fig.savefig("plots/lead_resistance_result.png",dpi=140); print("saved")
