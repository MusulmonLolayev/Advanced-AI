# Lecture 2 — on-screen labels (for approval)

Every Uzbek label the video shows, with its English counterpart, by section. Numbers are filled in from
`statistics/raw/l02_numbers.json` where a label has `{…}`. Narration lines are approved separately in `lecture02.md`.

## lecture02_kit.py

| Uzbek | English |
|---|---|
| jami | total |
| {n} talaba | {n} students |
| 0-qism · Shartli ehtimollik va erklilik | Part 0 · Conditional probability and independence |
| 1-qism · Bayes teoremasi | Part 1 · Bayes' theorem |
| velosipedli | bike |
| velosipedsiz | no bike |
| avtobusda | bus |
| avtobussiz | no bus |

## lecture02_s00.py

| Uzbek | English |
|---|---|
| Shartli ehtimollik, erklilik va Bayes teoremasi | Conditional probability, independence and Bayes' theorem |

## lecture02_s01.py

| Uzbek | English |
|---|---|
| «Juft son chiqdi» | “It's even.” |
| kubik oʻzgarmadi | the die did not change |
| bilganimiz oʻzgardi | what we know changed |
| Shartli ehtimollik | Conditional probability |
| «… boʻlgandagi» | “given” |
| yangi fazo = A | new sample space = A |
| P(spam ∣ «bepul sovrin») | P(spam ∣ “free prize”) |
| P(avtobusda ∣ velosipedsiz) | P(bus ∣ no bike) |
| Ulardan nechtasi avtobusda qatnaydi? | How many of them take the bus? |
| P(avtobusda) | P(bus) |
| velosipedli: {n} | bike: {n} |
| P(avtobusda ∣ velosipedli) | P(bus ∣ bike) |
| klassifikator | classifier |
| Faqat {n} ta velosipedsiz talabaga qaraymiz | Look only at the {n} students with no bike |
| surat | top |
| maxraj | bottom |
| «bepul sovrin!» | “free prize!” |

## lecture02_s02.py

| Uzbek | English |
|---|---|
| yoʻl boʻylab koʻpaytiramiz | multiply along the path |
| Avval avtobus, keyin velosiped | Bus first, then bike |
| Birinchi ikki shoxda qanday sonlar turadi? | What goes on the first two branches? |
| 1-bosqich: velosiped | stage 1: bike? |
| 2-bosqich: avtobus | stage 2: bus? |
| 2-bosqich 1-bosqichga bogʻliq | stage 2 depends on stage 1 |

## lecture02_s03.py

| Uzbek | English |
|---|---|
| 2-olish 1-olishga bogʻliq | the 2nd draw depends on the 1st |
| Ikkalasi ham oq? | Both white? |
| Bir xil rangli juft: ikkalasi qora yoki ikkalasi oq? | A matching pair: both black or both white? |
| P(ikkalasi qora) = ? | P(both black) = ? |
| berilganlar toʻplami | dataset |
| oʻqitish | training |
| test | test |
| har bir misol faqat bitta qismga tushadi | each example goes to one part only |
| ikkalasi oq | both white |
| juft | pair |
| yarimdan ham kam! | less than half! |
| 1-si qora | 1st black |
| 2-si qora ∣ 1-si qora | 2nd black ∣ 1st black |
| qaytarib | put back |
| qaytarmasdan | without replacement |
| qaytarib | with replacement |

## lecture02_s04.py

| Uzbek | English |
|---|---|
| Kontingentlik jadvali | Contingency table |
| Xatolar matritsasi | Confusion matrix |
| model: spam | model: spam |
| model: spam emas | model: not spam |
| haqiqiy: spam | true: spam |
| haqiqiy: spam emas | true: not spam |
| Talaba avtobusda qatnaydi. | A student takes the bus. |
| Velosipedi boʻlish ehtimoli qancha? | What is the probability they own a bike? |
| avtobus | bus |
| velosiped | bike |
| birgalikdagi | joint |
| marginal | marginal |
| shartli | conditional |

## lecture02_s05.py

| Uzbek | English |
|---|---|
| hamma talabalar | all students |
| Avtobusda qatnaydi | Takes the bus |
| erkli emas | not independent |
| hamma | all |
| koʻzoynakli | glasses |
| qator jami × ustun jami | row total × column total |
| umumiy son | grand total |
| kutilgan katak = | expected cell = |
| Erkli boʻlsa | If independent |
| Velosiped va avtobus erkli boʻlsin. | Suppose bike and bus were independent. |
| «Velosipedsiz, avtobusda» katagida nechta talaba? | How many students in “no bike, bus”? |
| {n} talaba koʻzoynak taqadi | {n} wear glasses |
| erkli | independent |
| y belgilanganlar ulushi | share of label y |
| model | model |
| hech narsa oʻrganmaydi | learns nothing |
| 1-guruh | group 1 |
| 2-guruh | group 2 |
| birlashtirilgan | pooled |
| jadvalda: | table: |
| kuzatilgan: | observed: |
| bogʻliq | dependent |
| xususiyat = 0 | feature = 0 |
| xususiyat = 1 | feature = 1 |

## lecture02_s06.py

| Uzbek | English |
|---|---|
| erkaklar | men |
| ayollar | women |
| Berkli, 1973-yil kuzi | Berkeley, autumn 1973 |
| hammasi | all six |
| Qayerga hujjat topshirishgan | Where they applied |
| qabul ulushi | admission rate |
| Simpson paradoksi | Simpson's paradox |
| umuman | overall |
| bitta fakultet ichida | within one department |
| tasvir uchun | illustration |
| berilganlar qanday tanlangan? | how were the data selected? |
| B kasalxonada umuman olganda kamroq bemor tuzaladi. | Hospital B has the worse overall recovery rate. |
| U har bir operatsiyada yaxshiroq boʻlishi mumkinmi? | Can it be better at every single operation? |
| magistraturaga qabul · eng katta oltita fakultet | graduate admissions · six largest departments |
| 1-guruh | group 1 |
| 2-guruh | group 2 |
| birlashtirilgan model | pooled model |
| eng ogʻir bemorlar | hardest cases |
| Ha | Yes |
| qiyin | hard |
| oson | easy |

## lecture02_s07.py

| Uzbek | English |
|---|---|
| Toʻla ehtimollik formulasi | The law of total probability |
| Model aniqligi | Model accuracy |
| katta guruh | large group |
| kichik guruh | small group |
| Shu formula bilan: avtobusda qatnamaslik ehtimoli = ? | P(no bus) with the same formula = ? |
| umumiy aniqlik | overall accuracy |
| tasvir uchun | illustration |

## lecture02_s08.py

| Uzbek | English |
|---|---|
| aprior ehtimollik | prior |
| Avtobusda qatnaydigan talabaning velosipedi yoʻq boʻlish ehtimoli = ? | P(no bike ∣ bus) = ? |
| Bayes teoremasi bilan hisoblaymiz | Use Bayes' theorem |
| Bayes teoremasi | Bayes' theorem |
| toʻla ehtimollik formulasi | law of total probability |
| haqiqatga oʻxshashlik | likelihood |
| aposterior ehtimollik | posterior |
| yomgʻir | rain |
| hoʻl yoʻlak | wet pavement |
| dalil | evidence |
| koʻcha yuvadigan mashina | street cleaner |
| aniq | certain |
| P(yomgʻir) | P(rain) |
| P(spam ∣ soʻzlar) | P(spam ∣ words) |
| ishonch | belief |
| dalil: berilganlar | evidence: data |
| yangilangan ishonch | updated belief |
| oʻlchash oson | easy to measure |
| bizga kerak | what we need |
| aprior | prior |
| aposterior | posterior |

## lecture02_s09.py

| Uzbek | English |
|---|---|
| musbat | positive |
| kasal | ill |
| test | test |
| testning xususiyati | a property of the test |
| bemorga kerak | what the patient wants |
| Prokuror xatosi | The prosecutor's fallacy |
| «Million begunoh odamdan faqat bittasi mos keladi» | “Only 1 innocent person in a million would match” |
| moslik | match |
| begunoh | innocent |
| har bir haqiqiy holatga ≈ {…} yolgʻon signal | ≈ {…} false alarms per real case |
| Firibgarlikni aniqlovchi model | Fraud detector |
| tasvir uchun | illustration |
| {…} kishidan biri kasal. | 1 person in {…} has the disease. |
| Test oʻsha: kasalni oʻtkazib yubormaydi, {…} yolgʻon signal. | Same test: never misses, {…} false alarms. |
| P(kasal ∣ musbat) = ? | P(ill ∣ positive) = ? |
| 100 kishidan 1 | 1 in 100 |
| 10 kishidan 1 | 1 in 10 |
| kasalligi aniq | known to be ill |
| + kasallik qanchalik keng tarqalgani | + how common the illness is |
| {…} kishidan biri kasal | 1 in {…} is ill |
| {…} kishi musbat | {…} test positive |
| {…} ning {…} i | {…} of {…} |
| {…} ning 100% i | 100% of {…} |
| sogʻlom : kasal = {…} : 1 | healthy : ill = {…} : 1 |
| {…} ta signal, {…} tasi haqiqiy | {…} alarms, {…} real fraud |
| test oʻsha-oʻsha | the same test |
| yolgʻon signal | false alarms |
| {…} kishi tekshirildi | {…} people tested |
| {…} kasal | {…} ill |
| {…} sogʻlom | {…} healthy |
| sogʻlom | healthy |

## lecture02_s10.py

| Uzbek | English |
|---|---|
| kasal | ill |
| musbat | positive |
| asosiy ulush = aprior ehtimollik | base rate = the prior |
| asosiy ulush (%) | how common the disease is (%) |
| P(kasal ∣ musbat), % | P(ill ∣ positive), % |
| deyarli hamma sogʻlom | almost everyone is well |
| musbat → boshqa, ikkinchi test | positive → a second, different test |
| model: doim «sogʻlom» | model: always “healthy” |
| Bayes teoremasi qayerda qaytadi | Where Bayes' theorem comes back |
| 2-maʼruza — xulosa | Lecture 2 — summary |
| {…} kishidan biri kasal. | 1 person in {…} is ill. |
| Model doim «sogʻlom» deydi. | The model always answers “healthy”. |
| Aniqlik = ? | Accuracy = ? |
| 6-maʼruza | Lecture 6 |
| Bayes xulosasi | Bayesian inference |
| 3-modul | Module 3 |
| Sodda Bayes / klassifikatori | Naive Bayes |
| 1-modul | Module 1 |
| Tasniflash / koʻrsatkichlari | Classification / metrics |
| Shart namunalar fazosini toraytiradi | A condition shrinks the sample space |
| Daraxt: shoxlar boʻylab koʻpaytiramiz · jadval: maxrajni tanlaymiz | Tree: multiply along branches · table: choose the denominator |
| Erklilik: shartli = oddiy · birlashtirish teskari qilishi mumkin | Independence: conditional = plain · pooling can reverse |
| Toʻla ehtimollik: vaznli oʻrtacha · Bayes: shartni teskari aylantiradi | Total probability: a weighted average · Bayes: turn the condition around |
| test oʻzgarmaydi | same test throughout |
| kasallik kamroq → foydasiz model yaxshiroq koʻrinadi | rarer disease → a useless model looks better |
| aniqlik | accuracy |
| topilgan kasallar | ill people found |
| 3-maʼruza · Diskret tasodifiy miqdorlar va asosiy taqsimotlar | Lecture 3 · Discrete random variables and key distributions |
| tugadi | the end |
| {…} kishidan 1 | 1 in {…} |
