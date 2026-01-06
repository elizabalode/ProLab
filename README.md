# Sabalansētas ēdienkartes plānošana

Mājaslapa, kur lietotājs ievada savus biometriskos datus (augums, svars, dzimums, vārds, uzvārds, vecums, cik aktīvs dzīvesveids), un sistēma automātiski ģenerē sabalansētu ēdienkarti, balstoties uz aprēķināto enerģijas patēriņu un uzturvielu mērķiem.

---

## Ievads

### Problēmas nostādne
Cilvēkiem bieži ir grūti pašiem aprēķināt nepieciešamo kaloriju daudzumu un izveidot sabalansētu ēdienkarti, jo tas prasa zināšanas uzturzinātnē un laiku atlasīt produktus. Tāpēc rodas vajadzība pēc rīka, kas automatizē kaloriju mērķa aprēķinu un piedāvā ēdienkarti pēc lietotāja datiem.

### Darba mērķis
Izstrādāt web lietotni, kas:
1. ievāc lietotāja biometriskos datus,
2. aprēķina kaloriju mērķi dienai,
3. ģenerē ēdienplānu (3 ēdienreizes) konkrētam datumam,
4. attēlo rezultātu pārlūkā.

### Novērtēšana
Novērtēt, vai sistēma:
- korekti apstrādā ievadi un saglabā lietotāju DB,
- atgriež plānu pēc `user_id` un `date`,
- pareizi saskaita kalorijas katrai ēdienreizei un kopējās kalorijas,
- strādā dažādiem lietotāju parametriem.

---

## Tehniskais risinājums

### Algoritms 
1. Aprēķina BMR pēc Mifflin–St Jeor formulas:
   - Vīrietis: `10*w + 6.25*h - 5*age + 5`
   - Sieviete: `10*w + 6.25*h - 5*age - 161`
2. Dienas kaloriju mērķis: `BMR * activity`
3. Ēdienplāna ģenerēšana:
   - ja plāns datumam jau ir DB → atgriež esošo
   - ja nav → izvēlas 3 ēdienus (brokastis/pusdienas/vakariņas) deterministiski pēc datuma (`seed = YYYYMMDD`)
4. Katras ēdienreizes kcal summa:
   - `kcal = grams * kcal_per_100g / 100`

---

## Konceptu modelis
<img width="1026" height="656" alt="image" src="https://github.com/user-attachments/assets/799e5748-39f2-4b87-ae6e-4f835a859e61" />
