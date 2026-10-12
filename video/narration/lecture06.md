# Lecture 6 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Bayes xulosasi) = sections 1–5,
Part 1 (Maksimal aposterior baho va qoʻshma aprior taqsimotlar) = sections 6–10. Each section: problem first → concept
as the answer → one AI use → a hands-on pause → the question the next section answers. The running example is the
slides' own: the 7:40 bus over a hundred mornings (the figure script's simulated stream, true on-time rate 0.70), then
Lecture 3's coffee-shop cups and a walk to the station.

**Rules applied:** berilganlar (data) / belgilanganlar (labels); "we", never "you" (only *Videoni toʻxtating*);
Latin letters spoken by their English names (key, es, ef, el); Greek letters keep theirs (teta, alfa, beta, tau,
sigma, lambda); numbers spelled for the ear, digits on screen. Screen labels are words only.
**Numbers:** every figure comes from `video/statistics/raw/l06_numbers.json` / `l06_figures.txt`
(`capture_l06.py`, unit-tested in `test_l06.py`). The hundred mornings are the figure script's own, regenerated from
its seed. No slide needed a fix.

**Terms to confirm** (new in this lecture):
- aprior taqsimot / aposterior taqsimot (prior / posterior as curves; Lecture 2's aprior / aposterior ehtimollik, now
  over every θ)
- **aposterior oraliq** (credible interval) and **ishonch oraligʻi** (confidence interval). These are kept apart on
  purpose: «ishonchli oraliq» for credible would sit one letter from «ishonch oraligʻi».
- chastotali yondashuv / Bayes yondashuvi (frequentist / Bayesian)
- nuqtaviy baho (point estimate) · maksimal aposterior baho (MAP estimate; the screen shows MAP) · aposterior oʻrtacha
  (posterior mean)
- qoʻshma aprior taqsimot (conjugate prior; qoʻshma as in qoʻshma kompleks son) · bashorat taqsimoti (predictive
  distribution)
- dispersiyaning teskarisi (precision, 1/variance). Not «aniqlik», which is accuracy.
- regulyarizatsiya (regularization) · jarima (penalty) · vazn soʻnishi (weight decay) · Rij / Lasso regressiyasi (Ridge
  / Lasso) · el ikki / el bir regulyarizatsiyasi (L2 / L1)
- dastlabki oʻqitish / qoʻshimcha oʻqitish (pretraining / fine-tuning) · Tompson usuli (Thompson sampling) · Kalman
  filtri · Laplas taqsimoti · axborot nazariyasi (information theory, Lecture 7)

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "6-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Oltinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda Bayes xulosasini oʻrganamiz, birinchi qismda esa maksimal aposterior baho va qoʻshma aprior taqsimotlar bilan tanishamiz.**
   *Hello, dear friends, and welcome to our sixth lecture. It also has two parts. In part zero we study Bayesian inference, and in part one we meet the MAP estimate and conjugate priors.*

## Part 0 — Bayes xulosasi
▸ part card "0-qism · Bayes xulosasi"

### 1-boʻlim · Section 1 — Nega aprior taqsimot kerak · Why we need a prior
1. **Beshinchi maʼruzada maksimal haqiqatga oʻxshashlik usuli berilganlarni eng yaxshi tushuntiradigan tetani tanladi va boshqa hech narsadan foydalanmadi. Berilganlar juda oz boʻlsa, bu falokat.**
   *In Lecture 5, maximum likelihood picked the theta that explains the data best, and used nothing else. With very little data, that is a disaster.*
2. **Tasavvur qilamiz: yangi koʻchaga koʻchib keldik. Dushanba kuni soat yetti qirqdagi avtobus kechikdi.**
   *Imagine we have just moved to a new street. On Monday, the seven forty bus is late.*
   ▸ a bus stop, a clock at 7:40, Monday's card: late
3. **Maksimal haqiqatga oʻxshashlik javobi: bitta tongda nol marta oʻz vaqtida, demak teta bahosi nol. Yaʼni bu avtobus hech qachon oʻz vaqtida kelmaydi. Bunga hech kim ishonmaydi.**
   *Maximum likelihood answers: on time zero times in one morning, so the estimate of theta is zero. This bus is never on time. Nobody believes that.*
   ▸ θ̂ = 0/1 = 0
4. **Ishonmaymiz, chunki dushanbagacha ham avtobuslar haqida nimadir bilardik. Maksimal haqiqatga oʻxshashlikda buni yozib qoʻyadigan joy yoʻq.**
   *We do not believe it, because we already knew something about buses before Monday. Maximum likelihood has nowhere to write that down.*
5. **Hayotda ham shunday: bitta bir yulduzli sharhi bor restoran bir yulduzli restoran emas, birinchi penaltini oʻtkaza olmagan oʻyinchi esa nol foizli penaltichi emas.**
   *Everyday life agrees: a restaurant with one one-star review is not a one-star restaurant, and a player who misses their first penalty is not a zero percent penalty taker.*
6. **Avval bilganimizni aprior taqsimot saqlaydi. Ikkinchi maʼruzada aprior ehtimollik bitta son edi. Endi u teta qabul qilishi mumkin boʻlgan har bir qiymat ustidagi egri chiziq.**
   *What we knew before is kept by the prior. In Lecture 2 the prior was one number. Now it is a curve over every value theta could take.*
7. **«Avtobus taxminan sakson foiz tongda oʻz vaqtida keladi, lekin aniq bilmayman» — bu Beta sakkiz, ikki egri chizigʻi. Goʻyo avval sakkiz marta oʻz vaqtida kelganini va ikki marta kechikkanini koʻrgandekmiz. Oʻrtachasi nol butun oʻndan sakkiz.**
   *"The bus is on time about eighty percent of mornings, but I am not certain": that is the Beta eight, two curve. It is as if we had already watched eight on-time and two late arrivals. Its mean is zero point eight.*
   ▸ the Beta(8, 2) curve over θ from 0 to 1, its mean marked
8. **Sunʼiy intellektda tavsiya tizimi ham shunday ishlaydi: yangi mahsulotning bitta bahosi boʻlsa, uni shu bitta bahoga qarab na koʻkka koʻtaradi, na koʻmib tashlaydi — avvalgi bilimiga tayanadi.**
   *In AI, a recommender works the same way: when a new product has a single rating, it neither praises it to the skies nor buries it on that one rating; it leans on what it already knew.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Dushanba avtobus oʻz vaqtida kelganida, maksimal haqiqatga oʻxshashlik nima degan boʻlardi?**
   *Let's try it ourselves. Pause the video. Had the bus been on time on Monday, what would maximum likelihood have said?*
10. **Bitta tongda bir marta oʻz vaqtida: baho bir. Yaʼni «bu avtobus hech qachon kechikmaydi». Bu ham bemaʼni.**
    *On time once in one morning: an estimate of one. "This bus is never late." Just as absurd.*
11. **Aprior taqsimot va dushanbaning dalili qanday birlashadi? Keyingi boʻlimda.**
    *How do the prior and Monday's evidence combine? The next section.*

### 2-boʻlim · Section 2 — Bayes formulasi — yangilash qoidasi · Bayes' rule as an update rule
1. **Ikkinchi maʼruzadagi Bayes formulasini olamiz, faqat endi teta noldan birgacha boʻlgan butun oraliqni qamraydi.**
   *We take Lecture 2's Bayes formula, only now theta ranges over the whole interval from zero to one.*
   ▸ p(θ | D) = p(D | θ) p(θ) / p(D), with "aposterior", "haqiqatga oʻxshashlik", "aprior" under the terms
2. **Haqiqatga oʻxshashlik har bir teta koʻrganimizni qanchalik yaxshi tushuntirishini aytadi. Dushanba avtobus kechikdi: kechikish ehtimoli bir minus teta, va u teta nolga teng boʻlganda eng katta.**
   *The likelihood says how well each theta explains what we saw. On Monday the bus was late: the chance of that is one minus theta, largest when theta is zero.*
   ▸ the line 1 − θ
3. **Maxrajdagi dalil ehtimolida teta yoʻq. U faqat egri chiziq ostidagi yuzani birga tenglaydigan son, shuning uchun uni tashlab, oxirida qayta masshtablaymiz.**
   *The evidence in the denominator has no theta in it. It is only the number that makes the area under the curve one, so we drop it and rescale at the end.*
   ▸ p(θ | D) ∝ p(D | θ) p(θ)
4. **Soʻz bilan aytsak: avval ishonganimizdan boshlaymiz, har bir tetani dalilni qanchalik yaxshi tushuntirishiga koʻpaytiramiz va qayta masshtablaymiz. Berilganlarni yomon tushuntiradigan qiymatlar pastga tushadi. Oʻrganish — aynan shu.**
   *In words: we start from what we believed, multiply each theta by how well it explains the evidence, and rescale. Values that explain the data badly get pushed down. That is learning.*
5. **Beta sakkiz, ikkini bir minus tetaga koʻpaytirsak, yana Beta chiqadi, faqat kechikishlar soni bittaga oshadi: Beta sakkiz, uch.**
   *Multiply Beta eight, two by one minus theta and a Beta comes out again, with the late count raised by one: Beta eight, three.*
   ▸ Beta(8, 2) × (1 − θ) → Beta(8, 3); the curve slides left
6. **Yangi oʻrtacha — sakkizni oʻn birga boʻlamiz: nol butun mingdan yetti yuz yigirma yetti. Bitta kechikkan avtobus ishonchimizni nol butun oʻndan sakkizdan shu songa tushirdi. Maksimal haqiqatga oʻxshashlik esa nolgacha sakradi.**
   *The new mean is eight divided by eleven: zero point seven two seven. One late bus moved our belief from zero point eight to that, while maximum likelihood jumped all the way to zero.*
   ▸ prior mean 0.80 → posterior mean 0.727; the MLE at 0
7. **Sunʼiy intellektda har bir qoʻshimcha oʻqitilgan model ham shunday yangilanish: dastlabki oʻqitish matn haqida aprior ishonch qoldiradi, qoʻshimcha oʻqitish esa uni bizning berilganlarimizning haqiqatga oʻxshashligiga koʻpaytiradi.**
   *In AI, every fine-tuned model is such an update: pretraining leaves a prior belief about what text looks like, and fine-tuning multiplies it by the likelihood of our data.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Dushanba avtobus oʻz vaqtida kelganida, Beta sakkiz, ikki qanday yangilanardi va oʻrtachasi qancha boʻlardi?**
   *Let's try it ourselves. Pause the video. Had the bus been on time on Monday, how would Beta eight, two update, and what would its mean be?*
9. **Oʻz vaqtida kelishlar soni bittaga oshadi: Beta toʻqqiz, ikki. Oʻrtachasi — toʻqqizni oʻn birga boʻlamiz: nol butun mingdan sakkiz yuz oʻn sakkiz.**
   *The on-time count rises by one: Beta nine, two. Its mean is nine divided by eleven: zero point eight one eight.*
10. **Avtobusni yuz tong kuzatsak nima boʻladi? Keyingi boʻlimda.**
    *What happens if we watch the bus for a hundred mornings? The next section.*

### 3-boʻlim · Section 3 — Yuz tong · A hundred mornings
1. **Avtobusni yuz tong kuzatamiz. Bu yoʻnalishda avtobus aslida yetmish foiz tongda oʻz vaqtida keladi, lekin biz buni bilmaymiz.**
   *We watch the bus for a hundred mornings. On this route it really is on time seventy percent of the time, but we do not know that.*
   ▸ a hundred morning cards fill in, on time and late
2. **Har tongda aposterior taqsimot yangilanadi. Bitta tongdan keyin maksimal haqiqatga oʻxshashlik nol, aposterior oʻrtacha esa nol butun mingdan yetti yuz yigirma yetti.**
   *Each morning the posterior is updated. After one morning, maximum likelihood says zero, and the posterior mean zero point seven two seven.*
   ▸ the table: mornings, on time, MLE, posterior mean; first row
3. **Oʻn tongda oltitasi oʻz vaqtida: maksimal haqiqatga oʻxshashlik nol butun oʻndan olti, aposterior oʻrtacha nol butun oʻndan yetti. Oʻttiz tongda yigirma ikkitasi: nol butun mingdan yetti yuz oʻttiz uch va nol butun yuzdan yetmish besh.**
   *In ten mornings six were on time: maximum likelihood zero point six, posterior mean zero point seven. In thirty, twenty-two: zero point seven three three, and zero point seven five.*
4. **Yuz tongda oltmish sakkiztasi: nol butun yuzdan oltmish sakkiz va nol butun mingdan olti yuz toʻqson bir. Maksimal haqiqatga oʻxshashlik boshida u yoqdan bu yoqqa sakraydi, aposterior oʻrtacha esa oqilona oraliqdan chiqmaydi.**
   *In a hundred, sixty-eight: zero point six eight, and zero point six nine one. Maximum likelihood swings about early on, while the posterior mean never leaves the sensible range.*
   ▸ the two estimates traced over the hundred mornings; the posterior curves tighten (prior, 1, 10, 30, 100)
5. **Beta sakkiz, ikki — kayfiyat emas. U aynan oʻn tonglik kuzatuvga teng: alfa qoʻshuv beta — oʻn. Aprior taqsimot — saqlangan dalil.**
   *Beta eight, two is not a mood. It is worth exactly ten mornings of watching: alpha plus beta is ten. A prior is stored evidence.*
6. **Shuning uchun toʻgʻri savol «aprior taqsimotim subyektivmi?» emas, balki «aprior taqsimotim nechta kuzatuvga teng?».**
   *So the honest question is not "is my prior subjective?" but "how many observations is my prior worth?"*
7. **Maksimal haqiqatga oʻxshashlik ham aprior taqsimotsiz emas: u tekis Beta bir, bir kabi ishlaydi, yaʼni noldan birgacha har bir ulush bir xil ehtimolli degan ishonch bilan. Bu ham tanlov, faqat aytilmagan.**
   *Maximum likelihood is not free of priors either: it behaves like a flat Beta one, one, the belief that every rate from zero to one is equally plausible. That is also a choice, just an unstated one.*
   ▸ the flat Beta(1, 1) line beside Beta(8, 2)
8. **Sunʼiy intellektda yangi reklamaning bosilish ulushi shunday baholanadi: bir necha koʻrsatuvdan keyin uni nol yoki bir deb eʼlon qilmaslik uchun oldingi reklamalardan olingan aprior taqsimot qoʻshiladi.**
   *In AI, a new ad's click rate is estimated this way: so that a few impressions do not declare it zero or one, a prior taken from earlier ads is added.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beta sakkiz, ikkidan boshladik. Oʻn tongda oltitasi oʻz vaqtida keldi, toʻrttasi kechikdi. Aposterior taqsimot qanday va uning oʻrtachasi qancha?**
   *Let's try it ourselves. Pause the video. We started from Beta eight, two. In ten mornings, six were on time and four late. What is the posterior, and what is its mean?*
10. **Sakkiz qoʻshuv olti va ikki qoʻshuv toʻrt: Beta oʻn toʻrt, olti. Oʻrtachasi — oʻn toʻrtni yigirmaga boʻlamiz: nol butun oʻndan yetti. Jadvaldagi ikkinchi qator.**
    *Eight plus six and two plus four: Beta fourteen, six. Its mean is fourteen divided by twenty: zero point seven. The table's second row.*
11. **Bitta son qanchalik ishonchli ekanimizni aytmaydi. Buni qanday koʻrsatamiz? Keyingi boʻlimda.**
    *One number does not say how sure we are. How do we show that? The next section.*

### 4-boʻlim · Section 4 — Aposterior oraliq · The credible interval
1. **«Avtobus yetmish foiz tongda oʻz vaqtida keladi» degan gap oʻn tongdan keyin ham, oʻn ming tongdan keyin ham bir xil eshitiladi. Bitta son qanchalik ishonchli ekanimizni aytmaydi.**
   *"The bus is on time seventy percent of the time" sounds the same after ten mornings and after ten thousand. One number cannot say how sure we are.*
2. **Aposterior oraliq — aposterior taqsimot yuzasining maʼlum ulushini, masalan toʻqson besh foizini oʻz ichiga olgan teta oraligʻi. Odatda markaziy toʻqson besh foiz olinadi.**
   *A credible interval is the stretch of theta that holds a stated share of the posterior's area, say ninety-five percent. The central ninety-five percent is the usual choice.*
   ▸ the posterior with its central 95 % shaded
3. **Oʻn tongdan keyin aposterior oʻrtacha nol butun oʻndan yetti, markaziy toʻqson besh foiz esa nol butun mingdan toʻrt yuz sakson sakkizdan nol butun mingdan sakkiz yuz yetmish toʻrtgacha. Bu avtobus ishonchsizmi yoki aʼlomi — hali chindan ham bilmaymiz.**
   *After ten mornings the posterior mean is zero point seven, and the central ninety-five percent runs from zero point four eight eight to zero point eight seven four. We genuinely do not yet know whether this bus is unreliable or excellent.*
   ▸ Beta(14, 6) shaded from 0.488 to 0.874
4. **Bu oraliqning kengligi nol butun yuzdan oʻttiz toʻqqiz.**
   *That interval is zero point three nine wide.*
5. **Yuz tongdan keyin oʻrtacha nol butun mingdan olti yuz toʻqson bir, oraliq esa nol butun mingdan olti yuz ikkidan nol butun mingdan yetti yuz yetmish uchgacha.**
   *After a hundred mornings the mean is zero point six nine one, and the interval runs from zero point six zero two to zero point seven seven three.*
   ▸ Beta(76, 34) shaded from 0.602 to 0.773, under the first
6. **Sunʼiy intellektda aposterior taqsimoti keng model shunchaki taxmin qilib qoʻya qolmaydi: odamdan soʻrashi yoki aynan shu misolni belgilab berishni soʻrashi mumkin.**
   *In AI, a model whose posterior is wide need not just guess: it can ask a human, or ask for that very example to be labelled.*
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yuz tongdan keyingi oraliqning kengligi qancha?**
   *Let's try it ourselves. Pause the video. How wide is the interval after a hundred mornings?*
8. **Nol butun mingdan yetti yuz yetmish uchdan nol butun mingdan olti yuz ikkini ayiramiz: nol butun yuzdan oʻn yetti. Oraliq ikki baravardan ham koʻproq toraydi. Oʻrganish — aynan shu torayish.**
   *Zero point seven seven three minus zero point six zero two: zero point one seven. The interval narrowed by more than half. That narrowing is the learning.*
9. **Turli aprior taqsimotdan boshlagan kuzatuvchilar bir xil xulosaga keladimi? Keyingi boʻlimda.**
    *Do observers who start from different priors reach the same conclusion? The next section.*

### 5-boʻlim · Section 5 — Aprior taqsimot qachon ahamiyatsiz boʻladi · When the prior stops mattering
1. **Uchta qoʻshni aynan bir xil yuz tongni kuzatadi, lekin har xil ishonchdan boshlaydi.**
   *Three neighbours watch the same hundred mornings, from different starting beliefs.*
2. **Birinchisining fikri yoʻq: tekis Beta bir, bir. Ikkinchisi — biz: Beta sakkiz, ikki, oʻn tongga teng. Uchinchisi qaysar: Beta sakson, yigirma, yuz tongga teng.**
   *The first has no opinion: a flat Beta one, one. The second is us: Beta eight, two, worth ten mornings. The third is stubborn: Beta eighty, twenty, worth a hundred mornings.*
   ▸ the three prior curves, then the three posteriors after the same 100 mornings
3. **Yuz tongdan keyin tekis boshlagan qoʻshni nol butun mingdan olti yuz yetmish oltida, biz esa nol butun mingdan olti yuz toʻqson birda toʻxtaymiz. Egri chiziqlar deyarli ustma-ust: boshqaruvni berilganlar oldi.**
   *After the hundred mornings, the flat neighbour ends at zero point six seven six and we end at zero point six nine one. The curves nearly coincide: the data has taken over.*
4. **Qaysar qoʻshnining aprior taqsimoti esa yuz tongga teng, yaʼni berilganlar bilan barobar.**
   *The stubborn neighbour's prior, though, is worth a hundred mornings: as much as the data.*
5. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yuz tongda oltmish sakkiztasi oʻz vaqtida, oʻttiz ikkitasi kechikdi. Qaysar qoʻshnining aposterior taqsimoti qanday va oʻrtachasi qancha?**
   *Let's try it ourselves. Pause the video. In a hundred mornings, sixty-eight were on time and thirty-two late. What is the stubborn neighbour's posterior, and its mean?*
6. **Beta bir yuz qirq sakkiz, ellik ikki. Oʻrtachasi — bir yuz qirq sakkizni ikki yuzga boʻlamiz: nol butun yuzdan yetmish toʻrt. Uning fikri rad etilmadi, faqat yarim yoʻlgacha oʻzgardi.**
   *Beta one hundred forty-eight, fifty-two. Its mean is one hundred forty-eight divided by two hundred: zero point seven four. Never overruled, only moved halfway.*
   ▸ 0.80 → 0.74, with the data's 0.68 beside it
7. **Amaliy qoida: key ta kuzatuvga teng aprior taqsimotni yengish uchun key dan bir necha baravar koʻp berilganlar kerak.**
   *A rule of thumb: a prior worth k observations needs a few times k to be overruled.*
8. **Endi tasodifiy narsa nima? Chastotali yondashuvda teta — oʻzgarmas nomaʼlum son, tasodifiy narsa esa berilganlar. Toʻqson besh foizlik ishonch oraligʻi — usul haqidagi gap: oyni koʻp marta takrorlasak, qurilgan oraliqlarning toʻqson besh foizi haqiqiy tetani oʻz ichiga oladi.**
   *Now, what is random? To a frequentist, theta is a fixed unknown number and the data is random. A ninety-five percent confidence interval is a statement about the procedure: repeat the month many times, and ninety-five percent of the intervals built would contain the true theta.*
9. **Bayes yondashuvida berilganlar — haqiqatan koʻrganimiz, ular oʻzgarmas, nomaʼlum narsa esa teta. Toʻqson besh foizlik aposterior oraliq shuni aytadi: shu aprior taqsimot va shu berilganlarda teta toʻqson besh foiz ehtimol bilan oraliq ichida.**
   *To a Bayesian, the data is what we actually saw, so it is fixed, and theta is what we are uncertain about. A ninety-five percent credible interval says: given this prior and this data, theta lies inside with probability ninety-five percent.*
10. **Odamlar ishonch oraligʻini aytganda, odatda aynan Bayes gapini nazarda tutishadi. Ikkala yondashuv ham xato emas: ular turli savolga javob beradi, berilganlar koʻp boʻlsa esa odatda mos tushadi — tekis aprior taqsimot buni koʻrsatdi.**
    *When people quote a confidence interval, they usually mean the Bayesian sentence. Neither framing is wrong: they answer different questions, and with plenty of data they usually agree, as the flat prior showed.*
11. **Sunʼiy intellektda shuning uchun ulkan berilganlar toʻplamida aprior taqsimot deyarli sezilmaydi, bir necha misolda esa deyarli hamma narsani u hal qiladi.**
    *In AI, that is why on a huge dataset the prior hardly shows, while with a handful of examples it decides almost everything.*
12. **Mana shu bilan nolinchi qismni tugatamiz. Lekin baʼzan butun egri chiziq emas, bitta son kerak. Uni qanday tanlaymiz? Birinchi qismda.**
    *That completes part zero. But sometimes we need one number, not a whole curve. How do we choose it? In part one.*

## Part 1 — Maksimal aposterior baho va qoʻshma aprior taqsimotlar
▸ part card "1-qism · Maksimal aposterior baho va qoʻshma aprior taqsimotlar"

### 6-boʻlim · Section 6 — Choʻqqi yoki muvozanat nuqtasi · MAP and the posterior mean
1. **Butun aposterior taqsimot — halol javob, lekin baʼzan harakat qilish kerak: jadval ilovasida faqat bitta songa joy bor, model esa har bir vazn uchun bitta qiymat talab qiladi.**
   *The whole posterior is the honest answer, but sometimes we must act: the timetable app has room for one number, and a model needs one setting for each weight.*
2. **Egri chiziqni bitta songa aylantirishning ikki yoʻli bor: uning choʻqqisini yoki muvozanat nuqtasini olamiz.**
   *There are two ways to collapse a curve to a number: we take its peak, or its balance point.*
3. **Maksimal aposterior baho — aposterior taqsimotning choʻqqisi, yaʼni eng ehtimolli teta. Aposterior oʻrtacha — muvozanat nuqtasi, uchinchi maʼruzadagi matematik kutilmaning oʻzi.**
   *The MAP estimate is the posterior's peak, the most probable theta. The posterior mean is its balance point, the same expectation as in Lecture 3.*
   ▸ θ̂_MAP = arg max p(θ | D),  E[θ | D]
4. **Beta alfa, beta uchun oʻrtacha — alfani alfa qoʻshuv betaga boʻlganimiz, choʻqqi esa alfa minus birni alfa qoʻshuv beta minus ikkiga boʻlganimiz.**
   *For a Beta alpha, beta, the mean is alpha over alpha plus beta, and the peak is alpha minus one over alpha plus beta minus two.*
   ▸ mean = α/(α + β),  MAP = (α − 1)/(α + β − 2)
5. **Oʻn tongdan keyin aposterior taqsimot Beta oʻn toʻrt, olti. Maksimal haqiqatga oʻxshashlik faqat berilganlarga qaraydi: nol butun oʻndan olti.**
   *After ten mornings the posterior is Beta fourteen, six. Maximum likelihood looks only at the data: zero point six.*
   ▸ Beta(14, 6) with three marks: MLE, posterior mean, MAP
6. **Aposterior oʻrtacha — oʻn toʻrtni yigirmaga boʻlamiz: nol butun oʻndan yetti. Maksimal aposterior baho — oʻn uchni oʻn sakkizga boʻlamiz: nol butun mingdan yetti yuz yigirma ikki.**
   *The posterior mean is fourteen over twenty: zero point seven. The MAP estimate is thirteen over eighteen: zero point seven two two.*
7. **Ikki Bayes javobi yuqoriroq, chunki ular oʻnta aprior tongni ham olib yuradi. Choʻqqi oʻrtachadan oʻngda, chunki bu taqsimotning dumi chapga choʻzilgan. Taqsimot simmetrik boʻlsa, ular ustma-ust tushadi.**
   *Both Bayesian answers sit higher, because they also carry the ten prior mornings. The peak is right of the mean because this posterior's tail stretches left. On a symmetric posterior the two coincide.*
8. **Sunʼiy intellektda neyron tarmoqni oʻqitish odatda aynan maksimal aposterior bahoni topadi: butun taqsimotni emas, eng ehtimolli vaznlarni.**
   *In AI, training a neural network usually finds exactly a MAP estimate: not the whole distribution, but the most probable weights.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yuz tongdan keyin aposterior taqsimot Beta yetmish olti, oʻttiz toʻrt. Maksimal aposterior baho qancha?**
   *Let's try it ourselves. Pause the video. After a hundred mornings the posterior is Beta seventy-six, thirty-four. What is the MAP estimate?*
10. **Yetmish beshni bir yuz sakkizga boʻlamiz: nol butun mingdan olti yuz toʻqson toʻrt. Oʻrtachaga juda yaqin, chunki berilganlar koʻp va taqsimot deyarli simmetrik.**
    *Seventy-five divided by one hundred and eight: zero point six nine four. Very close to the mean, because the data is plentiful and the posterior nearly symmetric.*
11. **Nega Beta ni koʻpaytirganda yana Beta chiqdi? Keyingi boʻlimda.**
    *Why did multiplying a Beta give a Beta again? The next section.*

### 7-boʻlim · Section 7 — Qoʻshma aprior taqsimot · Conjugate priors: updating is counting
1. **Aprior egri chiziqni haqiqatga oʻxshashlikka koʻpaytirish oson. Uni yuzasi bir boʻladigan qilib qayta masshtablash esa integral talab qiladi, va koʻp hollarda bu integralning formulasi yoʻq.**
   *Multiplying a prior curve by a likelihood is easy. Rescaling it so its area is one needs an integral, and in most cases that integral has no formula.*
2. **Qoʻshma aprior taqsimot — aposterior taqsimoti xuddi oʻsha oilaga qaytib tushadigan aprior taqsimot. Unda integralga tegmaymiz, faqat parametrlarni yangilaymiz.**
   *A conjugate prior is one whose posterior lands back in the same family. Then we never touch the integral; we just update the parameters.*
3. **Har tongda egri chiziqni qaytadan chizish oʻrniga hisoblagichga bir qoʻshamiz.**
   *Instead of redrawing a curve every morning, we add one to a counter.*
4. **Qoida: Beta alfa, betaga es ta muvaffaqiyat va ef ta muvaffaqiyatsizlik qoʻshilsa, Beta alfa qoʻshuv es, beta qoʻshuv ef chiqadi.**
   *The rule: Beta alpha, beta, plus s successes and f failures, gives Beta alpha plus s, beta plus f.*
   ▸ Beta(α, β) + s, f → Beta(α + s, β + f)
5. **Avtobus: Beta sakkiz, ikkidan boshlaymiz. Oʻttiz tongda yigirma ikkitasi oʻz vaqtida, sakkiztasi kechikdi: Beta oʻttiz, oʻn. Oʻrtachasi — oʻttizni qirqqa boʻlamiz: nol butun yuzdan yetmish besh.**
   *The bus: we start from Beta eight, two. In thirty mornings, twenty-two on time and eight late: Beta thirty, ten. Its mean is thirty over forty: zero point seven five.*
   ▸ two counters: 8 + 22 = 30, 2 + 8 = 10
6. **Demak alfa va beta — shunchaki oʻz vaqtida kelgan va kechikkan tonglar soni: boshida bor boʻlganlari qoʻshuv koʻrganlarimiz. «Oʻn tongga teng» degan son parametrlarning oʻzida turibdi.**
   *So alpha and beta are just counts of on-time and late mornings: the ones we started with plus the ones we saw. The "worth ten mornings" is sitting in the parameters themselves.*
7. **Ertaga avtobus oʻz vaqtida keladimi? Buning uchun bitta tetani tanlash shart emas: bashoratni har bir teta boʻyicha, unga ishonchimiz bilan tortib, oʻrtachalaymiz. Bu bashorat taqsimoti.**
   *Will the bus be on time tomorrow? For that we need not pick one theta at all: we average the prediction over every theta, weighted by how much we believe it. That is the predictive distribution.*
   ▸ p(yangi | D) = ∫ p(yangi | θ) p(θ | D) dθ
8. **Beta uchun bu oʻrtacha aposterior oʻrtachaning oʻzi.**
   *For a Beta, this average is just the posterior mean.*
9. **Sunʼiy intellektda Tompson usuli aynan shu hisoblagichlardan foydalanadi: har bir variant uchun uning Beta taqsimotidan bitta tetani tasodifiy oladi va eng kattasini tanlaydi. Qoʻshma aprior taqsimot tufayli buni har qadamda qilsa boʻladi.**
   *In AI, Thompson sampling uses exactly these counters: for each option it draws one theta at random from its Beta and picks the largest. Conjugacy makes that cheap enough to do at every step.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beta sakkiz, ikkidan boshlab, yuz tongda oltmish sakkiztasi oʻz vaqtida, oʻttiz ikkitasi kechikdi. Aposterior taqsimot qanday va ertaga oʻz vaqtida kelish ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. Starting from Beta eight, two, in a hundred mornings sixty-eight were on time and thirty-two late. What is the posterior, and the chance the bus is on time tomorrow?*
11. **Beta yetmish olti, oʻttiz toʻrt. Ertangi bashorat — uning oʻrtachasi: nol butun mingdan olti yuz toʻqson bir.**
    *Beta seventy-six, thirty-four. Tomorrow's prediction is its mean: zero point six nine one.*
12. **Javoblar ikkitadan koʻp boʻlsa-chi? Keyingi boʻlimda.**
    *What if there are more than two answers? The next section.*

### 8-boʻlim · Section 8 — Dirixle va kategorial taqsimot · Dirichlet–categorical
1. **Uchinchi maʼruzada Dirixle taqsimotining alfasi koʻrilgan buyurtmalarni sanaydi va yangilash — sanash, degan edik. Endi buning sababini koʻramiz.**
   *In Lecture 3 we said the Dirichlet's alpha counts orders already seen, and that updating is counting. Now we see why.*
2. **Qoida: Dirixle taqsimotida har bir javobning soni oʻz alfasiga qoʻshiladi.**
   *The rule: in a Dirichlet, each answer's count is added to its own alpha.*
   ▸ Dir(α₁, …, α_k) + n₁, …, n_k → Dir(α₁ + n₁, …, α_k + n_k)
3. **Qahvaxona: aprior taqsimot Dirixle nol butun oʻndan sakkiz, ikki, bir butun oʻndan ikki — taxminan toʻrtta buyurtmaga teng. Keyingi qirqta buyurtma: yettita kichik, yigirma bitta oʻrta va oʻn ikkita katta stakan.**
   *The coffee shop: the prior is Dirichlet zero point eight, two, one point two, worth about four orders. The next forty orders: seven small, twenty-one medium and twelve large cups.*
   ▸ three counters: small, medium, large
4. **Aposterior taqsimot: Dirixle yetti butun oʻndan sakkiz, yigirma uch, oʻn uch butun oʻndan ikki. Yigʻindisi qirq toʻrt.**
   *The posterior: Dirichlet seven point eight, twenty-three, thirteen point two. They add up to forty-four.*
5. **Oʻrtacha ulushlar: nol butun mingdan bir yuz yetmish yetti, nol butun mingdan besh yuz yigirma uch va nol butun oʻndan uch.**
   *The mean shares: zero point one seven seven, zero point five two three and zero point three.*
   ▸ each count over 44, as three bars
6. **Beta — shu qoidaning key ikkiga teng boʻlgan holi. Bitta oila, ikki nom.**
   *The Beta is simply this rule with k equal to two. One family, two names.*
7. **Sunʼiy intellektda mavzular modeli har bir hujjatning mavzular aralashmasiga Dirixle aprior taqsimotini qoʻyadi va uni soʻzlar soni bilan aynan shunday yangilaydi. Til modellaridagi har bir soʻz soniga bir qoʻshib silliqlash ham Dirixle aprior taqsimotining oʻzi.**
   *In AI, a topic model puts a Dirichlet prior on each document's mix of topics and updates it with word counts exactly like this. The add-one smoothing of language models is a Dirichlet prior too.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Navbatdagi buyurtma — katta stakan. Yangi parametrlar qanday va katta stakanning ulushi qancha?**
   *Let's try it ourselves. Pause the video. The next order is a large cup. What are the new parameters, and what is the large cup's share?*
9. **Yetti butun oʻndan sakkiz, yigirma uch, oʻn toʻrt butun oʻndan ikki. Katta stakanning ulushi — oʻn toʻrt butun oʻndan ikkini qirq beshga boʻlamiz: taxminan nol butun yuzdan oʻttiz ikki.**
   *Seven point eight, twenty-three, fourteen point two. The large cup's share is fourteen point two over forty-five: about zero point three two.*
10. **Nomaʼlum son uzluksiz boʻlsa-chi? Keyingi boʻlimda.**
    *What if the unknown is a continuous number? The next section.*

### 9-boʻlim · Section 9 — Bekatgacha yoʻl · The walk to the station
1. **Bekatgacha piyoda taxminan oʻn ikki daqiqa yuramiz, deb oʻylaymiz, uch daqiqa u yoki bu tomonga. Bu aprior taqsimot: oʻrtachasi oʻn ikki, standart chetlanishi uch boʻlgan normal taqsimot.**
   *We think the walk to the station takes about twelve minutes, give or take three. That is a prior: a normal distribution with mean twelve and standard deviation three.*
   ▸ the prior N(12, 3²)
2. **Yoʻlni toʻrt marta oʻlchaymiz: oʻn uch, oʻn toʻrt, oʻn olti va oʻn yetti daqiqa. Oʻrtachasi — oʻn besh. Bitta yurish taxminan uch daqiqaga oʻzgarib turadi.**
   *We time it four times: thirteen, fourteen, sixteen and seventeen minutes. The average is fifteen. A single walk varies by about three minutes.*
   ▸ four ticks on the minutes axis, their mean at 15
3. **Bu safar dispersiyaning teskarisi qoʻshiladi. Aprior taqsimot toʻqqizdan birni, toʻrtta oʻlchov esa toʻqqizdan toʻrtni olib keladi. Aposterior oʻrtacha — oʻn ikki va oʻn beshning shu ogʻirliklar bilan olingan oʻrtachasi: oʻn toʻrt butun oʻndan toʻrt.**
   *This time, inverse variances add. The prior brings one ninth and the four timings bring four ninths. The posterior mean is the average of twelve and fifteen with those weights: fourteen point four.*
   ▸ μ̂ = (1/9 · 12 + 4/9 · 15) / (1/9 + 4/9) = 14.4
4. **Aposterior standart chetlanish — toʻqqizni beshga boʻlib, ildiz olamiz: bir butun yuzdan oʻttiz toʻrt daqiqa.**
   *The posterior standard deviation is the square root of nine over five: one point three four minutes.*
   ▸ prior, the timings' curve and the posterior on one axis
5. **Bu misolda aprior tarqoqlik bitta oʻlchovning tarqoqligiga teng: ikkalasi ham uch daqiqa. Demak, taxminimiz aynan bitta qoʻshimcha oʻlchovga teng: bir karra oʻn ikkiga toʻrt karra oʻn beshni qoʻshib, beshga boʻlamiz — yana oʻn toʻrt butun oʻndan toʻrt.**
   *In this example the prior's spread equals one timing's spread: three minutes each. So our hunch counts as exactly one extra timing: one times twelve plus four times fifteen, divided by five, is fourteen point four again.*
   ▸ (1 × 12 + 4 × 15) / (1 + 4) = 72/5 = 14.4
6. **Har bir aprior taqsimotga beriladigan savol bitta: u nechta kuzatuvga teng? Beta sakkiz, ikki — oʻn tongga, Dirixle — toʻrtta buyurtmaga, bu taxmin — bitta oʻlchovga. Noaniq aprior taqsimot oz kuzatuvga teng va tez yengiladi, ishonchlisi esa koʻpga teng va oson yengilmaydi.**
   *The one question to ask of any prior: how many observations is it worth? Beta eight, two is worth ten mornings, the Dirichlet four orders, this hunch one timing. A vague prior is worth few and is quickly overruled; a confident one is worth many and is not.*
7. **Ertangi yurish qancha davom etadi? Aposterior dispersiya bir butun oʻndan sakkiz, ertangi yurishning oʻz dispersiyasi esa toʻqqiz. Bashorat standart chetlanishi — oʻn butun oʻndan sakkizning ildizi: uch butun yuzdan yigirma toʻqqiz daqiqa.**
   *How long will tomorrow's walk take? The posterior variance is one point eight, and tomorrow's walk has its own variance of nine. The predictive standard deviation is the square root of ten point eight: three point two nine minutes.*
   ▸ √(1.8 + 9) = 3.29; the predictive curve, wider than the posterior
8. **Bu aposterior taqsimotdan kengroq, chunki oʻrtachani ham, ertangi kunni ham bilmaymiz. Parametr haqidagi noaniqlik va dunyodagi shovqin — model «bilmayman» deganda aynan shu ikkisini ajratadi.**
   *It is wider than the posterior, because we are unsure of the average and of tomorrow. Uncertainty about the parameter versus noise in the world: that split is how a model says "I do not know".*
9. **Sunʼiy intellektda robot yoki uchuvchisiz avtomobil oʻz joyini shunday aniqlaydi: oldingi bahosini va sensorning yangi oʻlchovini dispersiyalarining teskarisi bilan tortib birlashtiradi. Bu Kalman filtri.**
   *In AI, a robot or a self-driving car locates itself this way: it combines its previous estimate with a new sensor reading, weighted by their inverse variances. That is the Kalman filter.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Aprior standart chetlanish bir butun oʻndan besh boʻlsa-chi? Bu taxmin nechta oʻlchovga teng va aposterior oʻrtacha qancha?**
    *Let's try it ourselves. Pause the video. What if the prior's standard deviation were one point five? How many timings is the hunch worth, and what is the posterior mean?*
11. **Toʻqqizni ikki butun yuzdan yigirma beshga boʻlamiz: toʻrt. Taxmin toʻrtta oʻlchovga teng. Toʻrt karra oʻn ikkiga toʻrt karra oʻn beshni qoʻshib, sakkizga boʻlamiz: oʻn uch butun oʻndan besh.**
    *Nine divided by two point two five: four. The hunch is worth four timings. Four times twelve plus four times fifteen, divided by eight: thirteen point five.*
12. **Model vaznlariga aprior taqsimot qoʻysak nima boʻladi? Keyingi boʻlimda.**
    *What happens when we put a prior on a model's weights? The next section.*

### 10-boʻlim · Section 10 — Aprior taqsimot — bu jarima · A prior is a penalty
1. **Aposterior taqsimotni maksimallashtirish — uning minus logarifmini minimallashtirish demak. Logarifm esa koʻpaytmani yigʻindiga ajratadi.**
   *Maximising the posterior means minimising minus its logarithm, and the logarithm splits the product into a sum.*
   ▸ ŵ = arg max p(D | w) p(w) = arg min [ −log p(D | w) − log p(w) ]
2. **Birinchi had beshinchi maʼruzadan tanish: maqsad qiymatlaridagi shovqin normal boʻlsa, u kvadratik xatolar yigʻindisi.**
   *The first term we know from Lecture 5: with normal noise on the targets, it is the sum of squared errors.*
3. **Ikkinchi had — vaznlarga qoʻyilgan aprior taqsimot. Oʻrtachasi nol, standart chetlanishi tau boʻlgan normal taqsimot vaznlar kvadratlarining yigʻindisini beradi, ikki tau kvadratga boʻlingan holda.**
   *The second term is the prior on the weights. A normal prior with mean zero and standard deviation tau gives the sum of the squared weights, divided by two tau squared.*
4. **Ikkalasini qoʻshib, oʻzgarmas sonlarni tashlaymiz: kvadratik xato qoʻshuv lambda karra vaznlar kvadratlarining yigʻindisi. Bunda lambda — sigma kvadratni tau kvadratga boʻlganimiz.**
   *Adding them and dropping the constants: squared error plus lambda times the sum of squared weights, where lambda is sigma squared over tau squared.*
   ▸ boxed: ŵ = arg min Σ (yᵢ − ŷᵢ)² + λ‖w‖²,  λ = σ²/τ²
5. **Bu Rij regressiyasi, vazn soʻnishi, el ikki regulyarizatsiyasi. Jarimani hech kim oʻylab topmagan: u aprior taqsimotdan kelib chiqdi.**
   *That is ridge regression, weight decay, L2 regularisation. Nobody invented the penalty: it fell out of a prior.*
6. **Formula oʻzi gapiradi: aprior taqsimot torroq, yaʼni tau kichik boʻlsa — jarima kattaroq. Berilganlar shovqinliroq, yaʼni sigma katta boʻlsa — jarima yana kattaroq.**
   *The formula speaks for itself: a tighter prior, a small tau, means a bigger penalty. Noisier data, a big sigma, means a bigger penalty too.*
7. **Tau ikki boʻlganda jarima koeffitsiyenti nol butun mingdan bir yuz yigirma besh, tau nol butun oʻndan besh boʻlganda esa ikki: oʻn olti baravar ogʻirroq.**
   *At tau equal to two the penalty coefficient is zero point one two five; at tau equal to zero point five it is two: sixteen times heavier.*
   ▸ left: three priors narrowing (τ = 2, 1, 0.5); right: their penalty parabolas steepening
8. **Aprior taqsimotni almashtirsak, jarima ham almashadi. Laplas aprior taqsimoti vaznlar modullarining yigʻindisini beradi: bu Lasso, el bir regulyarizatsiyasi. Uning jarimasi nolda burchak hosil qiladi, shuning uchun el bir vaznlarni aynan nolga tushiradi, el ikki esa tushirmaydi.**
   *Swap the prior and you swap the penalty. A Laplace prior gives the sum of the weights' absolute values: that is Lasso, L1 regularisation. Its penalty has a corner at zero, which is exactly why L1 drives weights to exactly zero and L2 does not.*
   ▸ the Laplace prior and its V-shaped penalty beside the Gaussian's parabola
9. **Sunʼiy intellektda deyarli har bir yoʻqotish funksiyasidagi regulyarizatsiya hadi — yashiringan aprior taqsimot. Birinchi modulda Rij va Lasso ikki foydali usul sifatida keladi. Aslida ular ikki aprior taqsimot.**
   *In AI, the regularisation term in almost every loss function is a prior in disguise. Module 1 brings Ridge and Lasso in as two useful tricks. They are two priors.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Sigma ikki, tau bir. Lambda qancha?**
    *Let's try it ourselves. Pause the video. Sigma is two and tau is one. What is lambda?*
11. **Toʻrtni birga boʻlamiz: toʻrt.**
    *Four divided by one: four.*
12. **Keling, maʼruzani yakunlaylik. Bayes formulasi — yangilash qoidasi: aposterior taqsimot aprior taqsimot karra haqiqatga oʻxshashlikka proporsional. Aprior taqsimot — saqlangan dalil, va uning nechta kuzatuvga tengligini soʻraymiz. Aposterior taqsimot — javobning oʻzi, aposterior oraliq esa qanchalik ishonchli ekanimizni aytadi.**
    *Let's wrap up the lecture. Bayes' rule is an update rule: the posterior is proportional to the prior times the likelihood. A prior is stored evidence, and we ask how many observations it is worth. The posterior is the answer, and a credible interval says how sure we are.*
13. **Maksimal aposterior baho — choʻqqi, aposterior oʻrtacha — muvozanat nuqtasi. Qoʻshma juftliklarda yangilash — oddiy arifmetika: Beta va Dirixle sonlarni qoʻshadi, Gauss dispersiyalarning teskarisini qoʻshadi. Normal aprior taqsimotli maksimal aposterior baho — aynan el ikki regulyarizatsiyasi, Laplas bilan esa el bir.**
    *The MAP estimate is the peak, the posterior mean the balance point. With conjugate pairs updating is plain arithmetic: Beta and Dirichlet add counts, the Gaussian adds inverse variances. MAP with a normal prior is exactly L2 regularisation; with a Laplace prior, L1.*
14. **Mana shu bilan oltinchi maʼruzamizni tugatamiz. Keyingi maʼruzada axborot nazariyasi bilan tanishamiz.**
    *That brings our sixth lecture to an end. In the next lecture, we meet information theory.*
