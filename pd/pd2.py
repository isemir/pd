import pandas as pd
import numpy as np
columns = ['A30', 'A60', 'A90', 'B120', 'B150', 'B180', 'B210', 'B240', 'B270', 'B300']
dfg = pd.DataFrame(index=columns, columns=columns) # postavljamo data frame za zbirnu matricu
df=pd.read_csv('d:\cloud\Dropbox\pd\svegrupe3105.csv') # ucitavamo sva kasnjenja  za jednu grupu unutar 12 mjeseci
#dfi=pd.read_csv('d:\cloud\Dropbox\pd\izlozenosti1.csv',thousands=",") # ucitavamo izlozenosti unutar 12 mjesec
df.replace(0,1,inplace=True) # mijenjamo kasnjenja sa 0 dana na 1 dan, ne utiče na tačnost, a olakasava krerianje petlji
df[df > 270] = 280 # mijenjamo kasnjenja veca od 270 dana na 280 dana, ne utiče na tačnost, a olakasava krerianje petlji
df1=df.ix[:, 1:15] # pravimo novi data frame koji ucitava samo kolone sa brojevima dana kasnjenja i grupom
nazivi = list(df1)
for z in range (1,7): # ova petlja rješeava sve homogenbe grup
    fajl='d:\cloud\Dropbox\pd\grupa'+str(z)+".xlsx"
    print(fajl)
    dfg = dfg.fillna(0)  # with 0s rather than NaNs

    for s in range (0,12): # racunamo pojedinace matrice i dodajemo ih na zbirnu  - s je brojac za tu petlju
        df2=df1[(df1.Grupa == z)]
     #   df2 = df2.ix[:, 1:14]
        df2=df2.dropna(subset=[nazivi[s]]) # pravimo novu matricu iz ucitanih podataka, na nacin da izbacujemo nul vrijednosti za mjesec koji racunamo
        df2.fillna(1,inplace=True) # ostale null vrijednosti mijenjamo sa jedinicama. Na ovaj način smo obezjedili da se oni koji otplaceni u toku mjeseca
        # tretiraju kao nula data kasnjenja

        l = 0
        m = 0
        i = 0
        j = 0

        df_ = pd.DataFrame(index=columns, columns=columns) # pravimo data frame za skupanje rezultata - pojedinacna matrica
        df_ = df_.fillna(0) # with 0s rather than NaNs

        for l in range(0,300,30): #pravimo kvadratnu matricu vrijednost svake ćelije odgovara prelazu ukupnog broja partija iz kasnjenja jedne
            # grupe u kasnjenje druge grupe
            j = 0
            for m in range(0,300,30):
                k=df2.ix[(df2.ix[:,s] >= l+1) & (df2.ix[:, s] <= l+30) & (df2.ix[:, s+1] >= m+1) & (df2.ix[:, s+1] <= m+30)].count()
                df_.set_value(i, j, k[0], takeable=True)
                j = j + 1
        #    df_.ix[i,:]=df_.ix[i,:]/df_.ix[i,:].sum() ovaj dio odkomentirati kad se radi pretvaranje u postotke na nivou pojedinacne matrice radi
        # radi ponderisanja sa izlozenotima. Zajdeno s tim odkomentarisati ovaj dio mnozenja sa izlozenoscu, komentarisati liniju ispod
            i=i+1

        dfg=dfg+df_#*izlozenost[s]

    for i in range (0,10):
        dfg.ix[i,:]=dfg.ix[i,:]/dfg.ix[i,:].sum() # pretvara brojeve u postotke za svaki redd matrice
        # Ponderisanje je obezbjeđeno na osnovu broja partije jer radimo samo jednu
    # matricu u kojoj saberemo sve slučajeve iz 12 pojedinačnih matrica

    dfpd=dfg.copy() # pravimo matricu za izračun defaulta
    dfpd.iloc[3:10,:]=0 #postavljamo apsorpiciju tako što dio matrice koji se odnosi na defaultere postavljamo na jediničnu matricu
    for i in range (3,10):
        dfpd.set_value(i, i,1, takeable=True)

    dfpd1= np.dot(dfpd,dfpd) # potenciramo matricu na vrijednost LIP-a
    if (z==5) or (z==6):
        lip=9
    else:
        lip=6
    print(lip)
    for i in range (1,lip):
        dfpd1= np.dot(dfpd1,dfpd)

    dfcr = np.dot(dfg,dfg) # potenciramo matricu na vrijednost LIP-a i za CR ovog puta sa originalnom DFG jer nam ne treba apsorpcija
    for i in range (1,6):
        dfcr= np.dot(dfcr,dfg)

    dfpdk=pd.DataFrame(dfpd1,index=columns, columns=columns) # pošto je dfpd1 kao rezulat potenciranja tipa np.array vracamo ga u data frame
    dfcrd=pd.DataFrame(dfcr,index=columns, columns=columns) # pošto je dfcr kao rezulat potenciranja tipa np.array vracamo ga u data frame

    # dodavanje zbirne CR kolon
    cr=dfcrd.ix[:,0]+dfcrd.ix[:,1]+dfcrd.ix[:,2] # CR dobijamo sabiranjem non default kolona
    cr['A30':'B120']=cr['B120'] # CR za one koji nisu defaultu postavljameo na vrijednost prve default kategorije
    cr['B300']=0 # nema oporavka za one koji kasne preko 270 dana
    cr1=pd.DataFrame(cr,columns=['CR'])
    cr2 = pd.DataFrame(1-cr, columns=['1-CR'])
    #dodavanje zbirne PD kolono

    PD=dfpdk.ix[:,3]+dfpdk.ix[:,4]+dfpdk.ix[:,5]+dfpdk.ix[:,6]+dfpdk.ix[:,7]+dfpdk.ix[:,8]+dfpdk.ix[:,9] # PD dobijamo sabiranjem default kolona

    PD1=pd.DataFrame(PD,columns=['PD'])
    #PD2=PD*(1-cr)
    PDCR=pd.DataFrame(PD*(1-cr),columns=['PD*(1-CR)'])
    # print(PDCR.head(10))
    #print(pd.concat([dfcrd, cr1], axis=1).head(10))
    writer=pd.ExcelWriter(fajl)
    pd.concat([dfpdk, PD1,cr2,PDCR], axis=1).to_excel(writer,sheet_name='PD')
    pd.concat([dfcrd, cr1], axis=1).to_excel(writer,sheet_name='CR')

    writer.save()