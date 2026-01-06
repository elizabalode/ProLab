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

## Līdzīgo risinājumu pārskats

Ir pieejamas vairākas uztura un ēdienkartes plānošanas lietotnes, kas palīdz sekot līdzi kalorijām un uzturvielām. Tomēr daudzas no tām ir orientētas uz manuālu datu ievadi vai maksas funkcijām. Šajā darbā uzsvars ir uz vienkāršu procesu, tas ir lietotājs ievada biometriskos datus un uzreiz saņem ģenerētu ēdienkarti konkrētai dienai.

### MyFitnessPal
Plaši izmantota kaloriju uzskaites lietotne ar lielu produktu datubāzi un iespēju manuāli ievadīt dienā apēsto ēdienu. Priekšrocība ir plašs funkciju klāsts un datu apjoms, taču lietotājam bieži jāveic daudz manuālu darbību (produktu meklēšana, porciju ievade), un daļa iespēju ir ierobežotas bez maksas plāna.

### Yazio
Lietotne ar uzsvaru uz uztura mērķiem, svara kontroli un ēdienreižu plānošanu. Piedāvā ēdienkartes un receptes, tomēr pilnvērtīgai personalizācijai un papildu funkcijām bieži nepieciešams abonements.

### Mūsu projekta atšķirība

- minimāla ievade,
- automātiski aprēķina dienas kaloriju mērķi,
- ģenerē ēdienkarti konkrētam datumam un attēlo to pārlūkā,
- izmanto vienkāršu arhitektūru (Flask + SQLite + HTML/JS), lai risinājumu būtu viegli saprast un attīstīt.

Pašreizējā prototipā ēdienkarte tiek veidota no iepriekš definētiem ēdieniem/produktiem datubāzē, bet nākotnē risinājumu iespējams paplašināt ar uzturvielu sabalansēšanu, lietotāja preferencēm un lielāku produktu datu kopu.

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

---

## Tehnoloģiju steks

| Komponents | Tehnoloģija |
|---|---|
| Lietotnes tips | Web lietotne |
| Backend | Python (Flask) |
| Datubāze | SQLite (`app.db`) |
| DB piekļuve | Python `sqlite3` |
| Frontend | HTML, CSS, JavaScript |
| API | REST (JSON) |
| Datu formāts | JSON |

---

### Autori
- Adelīna Diāna Mālija
- Krišjānis Kugrēns
- Viola Jansone
- Elīza Balode
- Alens Niks Limanskis
