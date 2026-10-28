"""Megafauna scaling sums behind docs/proposals/megafauna-scaling.md (giants: mass, food, density; dragons: Damuth by physiology, age structure).

Run: uv run python docs/review/megafauna/scaling.py. Standalone; nothing in planet/ uses it.
"""
import numpy as np
ft=0.3048
# ---------- Marshall et al. 2021 intercepts (log10, M in g, per km2) ----------
# (checked against the paper: 2.99 is Table 1's mean, p. 284; the 2.1x steps and the ~35x herbivore step are in the text, p. 284;
#  the 240x below is Table 1's 2.5%-97.5% tail ratio, log10 a 1.80 to 4.18)
LA={"mammal carnivore":2.99-np.log10(2.1),"mesotherm (Marshall)":2.99,"varanid":2.99+np.log10(2.1),
    "mammal herbivore":2.99-np.log10(2.1)+np.log10(35)}
dens=lambda M,la: 10**la*(M*1000)**-0.75
sig=np.log10(240)/3.92
print("Marshall check T.rex 5200 kg:",dens(5200,2.99))
# ---------- FMR, Nagy et al. 1999 (kJ/d, M in g) ----------
fmr={"mammal":lambda M:4.82*(M*1e3)**0.734,"bird":lambda M:10.5*(M*1e3)**0.681,"reptile":lambda M:0.196*(M*1e3)**0.889}
kcal=lambda kj:kj/4.184
# ---------- GIANTS ----------
print("\nGIANTS")
ref_h,ref_m=1.778,75.0
G=[("hill",16,1.4,0.01),("stone",18,0.9,None),("fire",18,1.5,0.008),("frost",21,1.15,0.006),("cloud",24,1.0,0.005),("storm",26,1.1,0.005)]
print(f"{'kind':6}{'h m':>6}{'iso kg':>8}{'build kg':>9}{'robust kg':>10}{'kcal/d':>9}{'x human':>8}{'grain t/yr':>11}{'cows/yr':>8}{'fish t/yr':>10}{'forager 1/km2':>14}{'carniv 1/km2':>13}{'repo 1/km2':>11}")
hum=70*75**0.75*1.7
for k,h,b,rep in G:
    r=h*ft/ref_h; iso=ref_m*r**3; bm=iso*b; rob=ref_m*r**3.3*b
    M=bm; kc=70*M**0.75*1.7; yr=kc*365
    forager=0.1*(M/65)**-0.75  # human foragers ~0.1/km2 median
    carn=197.6*M**-0.88/100      # Carbone & Gittleman density fit (checked: PDF p. 2, 197.6 and -0.88)
    print(f"{k:6}{h*ft:6.1f}{iso:8.0f}{bm:9.0f}{rob:10.0f}{kc:9.0f}{kc/hum:8.1f}{yr/3400/1000:11.1f}{yr/625e3:8.0f}{yr/1200/1000:10.1f}{1/forager:14.0f}{1/carn:13.0f}{(1/rep if rep else float('nan')):11.0f}")
# ---------- DRAGONS: Damuth at a single mass ----------
print("\nDRAGON single-mass Damuth, 1 per X km2 (median; z of owner's 1/5000)")
for M in (2000,10000,20000,40000):
    row=[f"{M/1000:4.0f} t"]
    for n,la in LA.items():
        d=dens(M,la); z=(np.log10(1/5000)-np.log10(d))/sig
        row.append(f"{n}: 1/{1/d:,.0f} (z {z:+.1f})")
    print("  ".join(row))
for M in (2000,20000,40000):
    print(f"FMR {M/1000:.0f} t kcal/d:",{k:round(kcal(f(M))) for k,f in fmr.items()}, " reptile/mammal",round(fmr['reptile'](M)/fmr['mammal'](M),2))
print("Komodo 70kg reptile/mammal",round(fmr['reptile'](70)/fmr['mammal'](70),2))
# Carbone prey biomass needed per dragon (89.1 and -1.05 checked: PDF p. 2)
for M in (2000,20000):
    per10t=89.1*M**-1.05
    print(f"Carbone: {M/1000:.0f} t carnivore needs {10/per10t:,.0f} t prey standing biomass each")
# ---------- DRAGON age structure ----------
print("\nDRAGON age structure")
ages=np.arange(0,3001)
La=np.interp(ages,[0,5,100,800,1500,3000],[0.8,3,8,16,22,28])
mass=0.6*70*(La/2.6)**3
def run(mort,label):
    m=np.select([ages<=5,ages<=100,ages<=800],[mort[0],mort[1],mort[2]],mort[3])
    l=np.concatenate([[1],np.cumprod(1-m[:-1])])
    stage=np.select([ages<=5,ages<=100,ages<=800],[0,1,2],3)
    names=["wyrmling 0-5","young 6-100","adult 101-800","ancient 801+"]
    E=fmr['reptile'](mass)
    print(f"-- {label}: annual mortality {mort}")
    for s in range(4):
        sel=stage==s
        print(f"   {names[s]:15} count {l[sel].sum()/l.sum():6.1%}  biomass {(l*mass)[sel].sum()/(l*mass).sum():6.1%}  energy {(l*E)[sel].sum()/(l*E).sum():6.1%}  mass {mass[sel].min()/1000:6.2f}-{mass[sel].max()/1000:6.1f} t")
    post=ages>5
    eco=(l*mass)[post].sum()/l[post].sum()
    b=(ages>100)*1.0; T=(ages*l*b).sum()/(l*b).sum()
    # energy equivalence: budget of Damuth density at eco mass, spread over the whole age structure
    for n in ("mammal carnivore","mesotherm (Marshall)","varanid"):
        d=dens(eco,LA[n]); Ebud=d*fmr['reptile'](eco)
        d_all=Ebud/((l*E).sum()/l.sum())
        print(f"   {n:22} ecological mass {eco/1000:5.1f} t -> post-wyrmling 1/{1/d:,.0f} km2; all ages 1/{1/d_all:,.0f}; ancients 1/{1/(d_all*l[stage==3].sum()/l.sum()):,.0f} km2")
    print(f"   generation time (fecundity flat from 100) {T:.0f} yr; mass-weighted fecundity {(ages*l*b*mass).sum()/(l*b*mass).sum():.0f} yr")
run((0.20,0.015,0.0025,0.004),"base")
run((0.30,0.03,0.005,0.008),"harsher")
run((0.10,0.01,0.001,0.002),"gentler")
