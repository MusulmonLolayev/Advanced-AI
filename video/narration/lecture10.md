# Lecture 10 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides (`statistics/main.tex` order): Part 0 (Modelni
baholash) = sections 1–6, Part 1 (Gipotezalarni tekshirish va kalibrlash) = sections 7–10, with a short look back over
the whole module at the end of section 10, since this is Module 0's last lecture. Each section: problem first → concept as the answer → one AI
use → a hands-on pause → the question the next section answers. The running examples are the slides' own: the coffee
shop's twenty days of iced-coffee sales against the day's temperature (the figure script's simulated days, regenerated
from its seed), two menu layouts shown to sixty customers each, and two weather forecasters.

**Written to the depth rule from the start** (instructor, after Lecture 4): each idea from more than one side, and
the earlier lectures recapped where they are used. The angles: memorising past papers, and Lecture 1's sample against
population; the three sets as three questions, and the student who peeks at the exam; the error measure as Lecture 5's
mean squared error under a square root; bias and variance *measured* by refitting on 2,000 fresh twenty-day samples
(a straight line too high by three cups every time, a degree-9 curve right on average but scattering by twenty-four
cups at 30 °C); the noise floor of 2.5 cups; cross-validation picking the degree without touching the test set; the
bootstrap's "with replacement" as Lecture 2's socks put back, and its interval checked by Lecture 4's two-sigma rule;
Lecture 3's 90 % on a hundred examples; the p-value as Lecture 2's conditional probability, the permutation spread as a
standard error and Lecture 5's square root of n deciding when the gap becomes convincing; the prosecutor's fallacy
again; Type I errors as Lecture 2's 495 false alarms and its base rate; "at least one false alarm" as Lecture 1's
complement rule; calibration as Lecture 1's long-run share; temperature scaling on Lecture 3's softmax.

**Rules applied:** berilganlar (data); tarafkashlik va dispersiya (bias and variance, Lecture 5's approved terms);
"we", never "you" (only *Videoni toʻxtating*); Latin letters spoken by their English names (key, em, pi, ey, bi);
numbers spelled for the ear, digits on screen. Screen labels are words only (none are added to `labels.yaml` yet).
**Numbers:** every figure comes from `video/statistics/raw/l10_numbers.json` / `l10_figures.txt`
(`capture_l10.py`, unit-tested in `test_l10.py`). The sales days, bootstrap resamples, shuffles and forecasts are the
figure script's own, regenerated from its seeds. Every number the slides print checks out against the computation:
no slide needed a fix. (`statistics/main.tex` has a stray `m` after the commented-out
`\input{lectures/lecture10_evaluation.tex}`; harmless while commented, but it will print an "m" once enabled.)

**Terms to confirm** (new in this lecture):
- oʻqitish toʻplami / validatsiya toʻplami / test toʻplami (training / validation / test set; oʻqitish and test are
  already used in Lectures 1, 3 and 5)
- koʻphad darajasi (degree of a polynomial) · model sigʻimi (capacity) · ortiqcha moslashish (overfitting) ·
  egiluvchan (flexible)
- oʻrtacha kvadratik xatoning ildizi (RMSE; Lecture 5's oʻrtacha kvadratik xato under a root; the narration then says
  just «xato», in cups)
- tarafkashlik va dispersiya (bias–variance, Lecture 5's terms) · kamaytirib boʻlmaydigan shovqin (irreducible noise)
- kross-validatsiya (cross-validation) · key boʻlakli (k-fold) · **boʻlak** (a fold; «qism» is taken by the video's
  parts and «boʻlim» by its sections)
- butstrep (bootstrap) · qaytarib tanlash (resampling with replacement; Lecture 2's «qaytarmasdan» turned around) ·
  koʻrsatkich (a metric) · foiz punkt (percentage point)
- gipotezalarni tekshirish (hypothesis testing) · nol gipoteza / muqobil gipoteza (null / alternative hypothesis)
- **pi-qiymat** (p-value; the letter by its English name, as «zed-qiymat» in Lecture 4; the screen shows p-qiymat. It
  sits next to Lecture 3's «pi» for a Bernoulli probability, which is the same letter.)
- statistik ahamiyatli (statistically significant) · ahamiyatlilik chegarasi (significance threshold)
- permutatsiya testi (permutation test), with the verb «aralashtiramiz» (we shuffle)
- birinchi tur xato / ikkinchi tur xato (Type I / Type II error); yolgʻon signal (Lecture 2) and «farqni oʻtkazib
  yubordik» (a miss) · yolgʻon musbat / yolgʻon manfiy (false positive / negative)
- giperparametr (hyperparameter) · konfiguratsiya · ey-bi test (A/B test)
- kalibrlash / kalibrlangan (calibration / calibrated) · ishonchlilik diagrammasi (reliability diagram) · kalibrlash
  xatosi (calibration error) · oʻziga ortiqcha ishongan (overconfident) · sinoptik (forecaster)
- **softmaks harorati** (temperature scaling; «harorat» alone would collide with the day's temperature in the coffee
  example)
- qaror daraxti (decision tree) · key eng yaqin qoʻshni (k-NN) · xos vektor (eigenvector) · sodda Bayes klassifikatori
  (Naive Bayes) · mashinali oʻqitish (machine learning) · reyting jadvali (leaderboard)

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "10-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Oʻninchi maʼruzamizga xush kelibsiz. Bu statistika modulining soʻnggi maʼruzasi, va u ham ikki qismdan iborat. Nolinchi qismda modelni qanday baholashni oʻrganamiz, birinchi qismda esa gipotezalarni tekshirish va kalibrlash bilan tanishamiz.**
   *Hello, dear friends, and welcome to our tenth lecture. It is the last lecture of the statistics module, and it also has two parts. In part zero we learn how to evaluate a model, and in part one we meet hypothesis testing and calibration.*

## Part 0 — Modelni baholash
▸ part card "0-qism · Modelni baholash"

### 1-boʻlim · Section 1 — Nega test toʻplami kerak · Why we need a test set
1. **Shu paytgacha berilganlarni tavsifladik: oʻrtacha qiymat, taqsimot, baho. Lekin sunʼiy intellektda bizni boshqa savol qiziqtiradi: model hali koʻrmagan kunda qanday ishlaydi?**
   *So far we have described data: means, distributions, estimates. But in AI another question interests us: how will a model do on a day it has not yet seen?*
2. **Bir misol. Talaba oʻnta eski imtihon biletini yod oladi va hammasiga bexato javob beradi: yuz foiz. Bu ertangi imtihon haqida hech narsa aytmaydi, chunki ertangi bilet — u yod olmagan yagona bilet.**
   *An example. A student memorises ten past exam papers and answers every one perfectly: a hundred percent. That says nothing about tomorrow's exam, because tomorrow's paper is the only one they have not memorised.*
   ▸ ten paper cards, each ticked; one card face down, "ertaga"
3. **Qahvaxonamizga qaytamiz. Har kuni havo harorati va sotilgan muzli qahva stakanlari sonini yozib boramiz. Toʻrtinchi maʼruzada bu ikkisi birga oʻzgarishini koʻrgan edik.**
   *Back to our coffee shop. Every day we write down the day's temperature and the number of iced coffees sold. In Lecture 4 we saw that these two move together.*
4. **Yigirma kunlik berilganlar orqali egri chiziq oʻtkazamiz. Yetarlicha egiluvchan egri chiziq shu yigirma kunda bor-yoʻgʻi bir butun yuzdan qirq sakkiz stakan xato qiladi. Yangi qirq kunda esa — yigirma yetti butun oʻndan yetti stakan.**
   *We fit a curve through twenty days of data. A flexible enough curve is off by only one point four eight cups on those twenty days. On forty fresh days, by twenty-seven point seven cups.*
   ▸ the twenty dots and the degree-9 curve; two numbers: 1.48 (20 kun), 27.7 (40 yangi kun)
5. **Moslashtirilgan berilganlardagi xato hech narsaning bahosi emas. U faqat qanchalik tirishganimizni oʻlchaydi.**
   *The error on the data we fitted is not an estimate of anything. It only measures how hard we tried.*
6. **Birinchi maʼruzani eslaylik: oʻqitish toʻplami — tanlanma, model esa bosh toʻplamda, yaʼni hali kelmagan kunlarda ishlashi kerak. Model tanlanmaning tasodifiy xususiyatlarini ham yod olib qoʻysa, tanlanmadagi xato bosh toʻplamdagi xatoni koʻrsatmay qoʻyadi.**
   *Recall Lecture 1: the training set is a sample, and the model has to work on the population, the days still to come. If the model also memorises the sample's accidents, the error on the sample stops showing the error on the population.*
   ▸ the sample-and-population picture of Lecture 1: twenty dots inside the cloud of all days
7. **Shuning uchun xatoni model koʻrmagan berilganlarda oʻlchaymiz.**
   *That is why we measure error on data the model has not seen.*
8. **Sunʼiy intellektda katta til modeli oʻqitish matnlarini soʻzma-soʻz takrorlay olishi mumkin. Bu uning yangi savolga javob bera olishini isbotlamaydi — buni faqat u koʻrmagan savollar koʻrsatadi.**
   *In AI, a large language model may be able to repeat its training texts word for word. That does not prove it can answer a new question; only questions it has not seen can show that.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yangi kunlardagi xato yigirma kundagidan necha baravar katta?**
   *Let's try it ourselves. Pause the video. How many times larger is the error on the new days than on the twenty?*
10. **Yigirma yetti butun oʻndan yettini bir butun yuzdan qirq sakkizga boʻlamiz: taxminan oʻn toʻqqiz baravar.**
    *Twenty-seven point seven divided by one point four eight: about nineteen times.*
11. **Model koʻrmagan berilganlarni qanday ajratamiz va ulardan qanday foydalanamiz? Keyingi boʻlimda.**
    *How do we set aside data the model has not seen, and how do we use it? The next section.*

### 2-boʻlim · Section 2 — Oʻqitish, validatsiya va test toʻplamlari · Training, validation and test
1. **Berilganlarimizni uchta toʻplamga ajratamiz, va har birining oʻz vazifasi bor.**
   *We split our data into three sets, and each has its own job.*
2. **Oʻqitish toʻplami — model moslashtiriladigan berilganlar. Talabamiz misolida — mashq qiladigan eski biletlar.**
   *The training set is the data the model is fitted on. For our student, the past papers they practise with.*
3. **Validatsiya toʻplami — bir nechta nomzod modeldan birini tanlash uchun ajratilgan berilganlar: egri chiziq qanchalik egiluvchan boʻlsin, daraxt qanchalik chuqur boʻlsin. Talaba uchun bu — qaysi tayyorlanish usuli ishlayotganini koʻrsatadigan sinov imtihoni.**
   *The validation set is data held out to choose between candidate models: how flexible a curve, how deep a tree. For the student, it is the mock exam that shows which way of revising is working.*
4. **Test toʻplamiga esa oxirigacha qoʻl tegizilmaydi. Tanlangan model qanchalik yaxshi ekanini aytish uchun undan bir marta foydalanamiz. Bu — haqiqiy imtihon.**
   *The test set is left untouched until the very end. We use it once, to report how good the chosen model is. That is the real exam.*
   ▸ one bar split into three blocks: oʻqitish · validatsiya · test, the student's analogy under each
5. **Nega aynan uchta? Chunki har biri boshqa savolga javob beradi. Oʻqitish toʻplami: model qanday boʻlsin? Validatsiya: qaysi model yaxshiroq? Test: tanlangan model yangi kunda qanday ishlaydi?**
   *Why exactly three? Because each answers a different question. Training: what should the model be? Validation: which model is better? Test: how does the chosen model do on a new day?*
6. **Test toʻplamiga qarab model tanlasak, u validatsiya toʻplamiga aylanadi — va hisobot berish uchun hech narsa qolmaydi. Test toʻplami unga qarab tanlagan zahotimiz sarflanadi.**
   *If we choose a model by looking at the test set, it turns into a validation set, and nothing is left to report with. A test set is spent the moment we choose by it.*
7. **Boshqa tomondan qaraylik: imtihon savollarini oldindan koʻrib, tayyorlanish usulini shunga moslab tanlagan talabaning bahosi endi uning bilimini emas, savollarni oldindan koʻrganini oʻlchaydi.**
   *Look at it from the other side: a student who saw the exam questions in advance and chose how to revise to fit them gets a mark that no longer measures what they know, only that they saw the questions.*
8. **Sunʼiy intellektda musobaqalardagi reyting jadvallari test toʻplamining javoblarini yashirin saqlaydi va har bir jamoaga kuniga bir necha marta tekshirishga ruxsat beradi. Aks holda jamoalar test toʻplamining oʻziga moslashib olardi.**
   *In AI, competition leaderboards keep the test set's answers hidden and let each team check only a few times a day. Otherwise teams would end up fitting the test set itself.*
9. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Oʻnta egri chiziqni sinab koʻrdik va test toʻplamida xatosi eng kichigini tanladik. Uning test xatosini halol hisobot sifatida aytsa boʻladimi?**
   *Let's think it over. Pause the video. We tried ten curves and picked the one with the smallest error on the test set. Can we report its test error as an honest result?*
10. **Yoʻq. Test toʻplami tanlovda qatnashdi, demak u endi validatsiya toʻplami. Uning eng kichik xatosi — oʻnta urinishning eng omadlisi, shuning uchun haqiqiy xatodan pastroq chiqishi mumkin. Halol hisobot uchun yangi berilganlar kerak.**
    *No. The test set took part in the choice, so it is now a validation set. Its smallest error is the luckiest of ten tries, so it can come out below the true error. An honest report needs fresh data.*
11. **Egiluvchanroq egri chiziq nega yangi kunda yomonroq ishlaydi? Keyingi boʻlimda yigirma kunni yaqindan koʻramiz.**
    *Why does a more flexible curve do worse on a new day? In the next section we look at the twenty days up close.*

### 3-boʻlim · Section 3 — Yigirma kunlik savdo · Fitting twenty days of sales
1. **Qahvaxona yigirma kun davomida havo harorati va sotilgan muzli qahvani yozdi. Salqin kunlarda savdo deyarli oʻzgarmaydi, havo isiganda esa koʻtariladi.**
   *The shop recorded the temperature and the iced coffees sold for twenty days. On cool days sales hardly change; once it warms up, they climb.*
   ▸ the twenty dots, temperature across, cups up
2. **Ularga uch xil egri chiziq oʻtkazamiz. Koʻphad darajasi — egri chiziq qanchalik egila olishi. Daraja qancha katta boʻlsa, model sigʻimi shuncha katta.**
   *We fit three curves to them. A polynomial's degree is how much the curve can bend. The higher the degree, the greater the model's capacity.*
3. **Birinchi daraja — toʻgʻri chiziq. U egila olmaydi, shuning uchun tekis joyni ham, yuqoridagi qismni ham oʻtkazib yuboradi. Oʻqitish toʻplamidagi xato ikki butun yuzdan sakson toʻrt, testda — uch butun yuzdan oʻttiz uch.**
   *Degree one is a straight line. It cannot bend, so it misses both the flat stretch and the top. Error on the training set two point eight four, on the test set three point three three.*
4. **Uchinchi daraja haqiqiy shaklga ergashadi: ikki butun yuzdan uch va ikki butun yuzdan oltmish besh.**
   *Degree three follows the real shape: two point zero three and two point six five.*
5. **Toʻqqizinchi daraja deyarli har bir nuqtadan oʻtadi. Bunga erishish uchun u yigirma bir daraja atrofida hatto manfiy savdoni, taxminan minus ikki stakanni bashorat qiladi. Xato: oʻqitishda bir butun yuzdan qirq sakkiz, testda — yigirma yetti butun oʻndan yetti.**
   *Degree nine passes near every dot. To get there it even predicts negative sales, about minus two cups, near twenty-one degrees. Error: one point four eight in training, twenty-seven point seven on the test days.*
   ▸ the three fits over the dots; the degree-9 dip below zero circled
6. **Xatoni shunday oʻlchadik: har bir kunda bashoratdan haqiqiy savdoni ayiramiz, kvadratga oshiramiz, oʻrtachasini olamiz va ildizdan chiqaramiz. Bu beshinchi maʼruzadagi oʻrtacha kvadratik xatoning ildizi. Birinchi maʼruzadagi standart chetlanish kabi, ildiz uni yana stakanlarga qaytaradi.**
   *We measured the error like this: on each day subtract the real sales from the prediction, square, average, and take the square root. It is the square root of Lecture 5's mean squared error. Like Lecture 1's standard deviation, the root brings it back to cups.*
   ▸ √(mean of (ŷᵢ − yᵢ)²), in cups
7. **Ikki ustunga birga qaraylik. Oʻqitish xatosi daraja oshgan sari kamayadi. Test xatosi esa avval kamayadi, keyin keskin oshadi. Ular orasidagi farq — ortiqcha moslashish: model berilganlardagi qonuniyatni emas, shovqinni yod olgan.**
   *Let's look at the two columns together. Training error falls as the degree rises. Test error first falls, then shoots up. The gap between them is overfitting: the model has memorised the noise, not the pattern in the data.*
   ▸ a table: degree 1, 3, 9 × training, test
8. **Sunʼiy intellektda juda katta neyron tarmoq ham kichik berilganlar toʻplamini toʻliq yod olib qoʻya oladi. Shuning uchun oʻqitish paytida validatsiya xatosini kuzatib boramiz va u oʻsa boshlaganda oʻqitishni toʻxtatamiz.**
   *In AI, a very large neural network can also memorise a small dataset completely. That is why we watch the validation error during training and stop training when it starts to rise.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Uchinchi va toʻqqizinchi darajada test xatosi oʻqitish xatosidan qanchaga katta?**
   *Let's try it ourselves. Pause the video. At degree three and at degree nine, how much larger is the test error than the training error?*
10. **Uchinchi darajada — nol butun yuzdan oltmish ikki stakan. Toʻqqizinchi darajada — yigirma olti butun yuzdan yigirma besh. Birinchisi — kutilgan kichik farq, ikkinchisi — ortiqcha moslashish.**
    *At degree three, zero point six two cups. At degree nine, twenty-six point two five. The first is the small gap we expect; the second is overfitting.*
11. **Nega sigʻim maʼlum chegaradan keyin zarar qila boshlaydi? Keyingi boʻlimda.**
    *Why does capacity start to hurt past a certain point? The next section.*

### 4-boʻlim · Section 4 — Tarafkashlik va dispersiya · The bias–variance tradeoff
1. **Model ikki qarama-qarshi sababga koʻra xato qilishi mumkin, va birini tuzatsak, ikkinchisi kuchayadi.**
   *A model can be wrong for two opposite reasons, and fixing one makes the other worse.*
2. **Birinchisi — haddan tashqari qattiqlik. Toʻgʻri chiziq qancha berilganlar boʻlsa ham haqiqiy egri chiziqqa egila olmaydi va har safar bir xil tomonga xato qiladi. Bu — tarafkashlik, beshinchi maʼruzadagi tarafkash bahoning oʻzi.**
   *The first is being too rigid. However much data it gets, a straight line cannot bend to the real curve, and it is wrong in the same direction every time. That is bias, the same biased estimate as in Lecture 5.*
3. **Ikkinchisi — haddan tashqari egiluvchanlik. Toʻqqizinchi daraja oʻzi koʻrgan yigirma kunning shovqiniga ergashadi. Boshqa yigirma kunni koʻrsatsak, butunlay boshqa shakl chiqadi. Bu — dispersiya.**
   *The second is being too flexible. Degree nine chases the noise in whichever twenty days it saw. Show it twenty other days and a completely different shape comes out. That is variance.*
4. **Buni oʻlchab koʻrdik. Kompyuterda yigirma kunlik yangi tanlanmani ikki ming marta oldik va har safar egri chiziqni qaytadan oʻtkazdik. Yigirma besh darajada haqiqiy savdo taxminan oʻn uch stakan.**
   *We measured it. On the computer we drew a fresh twenty-day sample two thousand times and refitted the curve each time. At twenty-five degrees the true sales are about thirteen cups.*
   ▸ many thin refits of each degree over the true curve (black); a vertical line at 25 °C
5. **Toʻgʻri chiziq oʻrtacha oʻn olti stakan bashorat qiladi — har safar taxminan uch stakan koʻp. Bashoratlarining standart chetlanishi esa bir stakandan ham kam. Tarafkashlik katta, dispersiya kichik.**
   *The straight line predicts sixteen cups on average: about three cups too many, every time. The standard deviation of its predictions is under one cup. Big bias, small variance.*
6. **Toʻqqizinchi daraja oʻrtacha oʻn uch stakanga deyarli aniq tushadi. Lekin oʻttiz darajada, haqiqiy savdo yigirma yetti stakan atrofida boʻlganda, uning bashoratlarining standart chetlanishi yigirma toʻrt stakanga yetadi. Tarafkashlik kichik, dispersiya ulkan.**
   *Degree nine lands almost exactly on thirteen cups on average. But at thirty degrees, where the true sales are around twenty-seven cups, the standard deviation of its predictions reaches twenty-four cups. Small bias, huge variance.*
   ▸ at 25 °C: two clusters of predictions, one off-centre and tight, one centred; at 30 °C the degree-9 cluster spread wide
7. **Uchinchi sabab hech kimning aybi emas: bir xil haroratdagi ikki kun baribir har xil sotadi. Misolimizda bu shovqinning standart chetlanishi ikki yarim stakan.**
   *The third cause is nobody's fault: two days at the same temperature still sell different amounts. In our example that noise has a standard deviation of two and a half cups.*
8. **Demak, yangi berilganlardagi xato uchta qoʻshiluvchidan iborat: tarafkashlik kvadrati, dispersiya va kamaytirib boʻlmaydigan shovqin.**
   *So the error on new data is made of three terms: bias squared, variance, and irreducible noise.*
   ▸ xato = tarafkashlik² + dispersiya + shovqin, each term labelled
9. **Talaba misolida: oʻnta biletni yod olgan talabaning tarafkashligi kichik, dispersiyasi ulkan — yod olmagan savolga javobi tasodifiy. Har qanday savolga «vaziyatga bogʻliq» deb javob beradigan talabaning esa dispersiyasi kichik, tarafkashligi ulkan.**
   *For the student: the one who memorised ten papers has low bias and huge variance; their answer to a question they did not memorise is anyone's guess. The one who answers "it depends" to everything has low variance and huge bias.*
10. **Endi xatolar egri chizigʻini oʻqiymiz. Oʻqitish xatosi faqat kamayadi: ikki butun yuzdan sakson toʻrtdan bir butun yuzdan qirq yettigacha. Bu majburiy: sigʻim oshsa, oʻsha nuqtalarga har doim yaxshiroq moslasha oladi.**
    *Now we read the error curve. Training error only ever falls: from two point eight four down to one point four seven. It has to: with more capacity, the same points can always be fitted better.*
11. **Test xatosi esa uchinchi darajada eng past — ikki butun yuzdan oltmish besh — keyin oʻsadi: yettinchi darajada toʻrt butun oʻndan sakkiz, keyin yigirma ikki, yigirma sakkiz va oʻttiz toʻrt. Yoʻlda biroz tebranadi: qirq kun unchalik koʻp emas.**
    *Test error is lowest at degree three, two point six five, then climbs: four point eight at degree seven, then twenty-two, twenty-eight and thirty-four. It wobbles on the way: forty days is not many.*
    ▸ training and test error over degrees 1–10, best degree 3 dashed; 22, 28, 34 as arrows off the top
12. **Faqat oʻqitish xatosiga qarasak, oʻninchi daraja eng yaxshi modelimizdek koʻrinadi. Oʻqitish xatosi qachon toʻxtashni hech qachon aytmaydi — buni faqat model koʻrmagan berilganlar aytadi.**
    *Watching only the training error, degree ten looks like our best model ever. Training error never tells us when to stop; only data the model has not seen can.*
13. **Sunʼiy intellektda har bir modelning sigʻim tutqichi bor: qaror daraxtining chuqurligi, key eng yaqin qoʻshni usulidagi qoʻshnilar soni, neyron tarmoqning kengligi, jarima kuchi. Birinchi modulda daraxtlarni aynan shu sababga koʻra kesamiz: kesilmagan daraxt har bir nuqtani alohida bargga qoʻya oladi — bu boshqa kiyimdagi oʻninchi daraja.**
    *In AI, every model has a capacity dial: the depth of a decision tree, the number of neighbours in k-nearest neighbours, the width of a neural network, the strength of a penalty. In Module 1 we prune trees for exactly this reason: an unpruned tree can put every point in its own leaf, which is degree ten in different clothes.*
14. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Shovqin ikki yarim stakan. Uchinchi darajaning test xatosi undan qanchaga katta?**
    *Let's try it ourselves. Pause the video. The noise is two and a half cups. How much larger than that is degree three's test error?*
15. **Ikki butun yuzdan oltmish beshdan ikki yarimni ayiramiz: nol butun yuzdan oʻn besh. Uchinchi daraja deyarli imkon qadar yaxshi: xatosining katta qismi — hech kim kamaytira olmaydigan shovqin.**
    *Two point six five minus two and a half: zero point one five. Degree three is nearly as good as it gets: most of its error is noise that nobody can remove.*
16. **Lekin sigʻimni tanlash uchun alohida validatsiya toʻplami qimmat. Undan tejamliroq yoʻl bormi? Keyingi boʻlimda.**
    *But a separate validation set is an expensive way to choose the capacity. Is there a thriftier way? The next section.*

### 5-boʻlim · Section 5 — Kross-validatsiya · Cross-validation
1. **Validatsiya toʻplamini ajratib qoʻyish berilganlarni ikki marta isrof qiladi: bu kunlarda model oʻqitilmaydi, bir necha kundagi baho esa oʻzi shovqinli.**
   *Holding out a validation set costs data twice: the model is not trained on those days, and a score from a handful of days is itself noisy.*
2. **Key boʻlakli kross-validatsiya buni hal qiladi. Oʻqitish berilganlarini key ta teng boʻlakka boʻlamiz. Key minus bittasida oʻqitamiz, qolgan bittasida baholaymiz va har bir boʻlak bir martadan chetda qolguncha takrorlaymiz. Key ta bahoning oʻrtachasini olamiz.**
   *K-fold cross-validation solves this. We split the training data into k equal folds. We train on k minus one of them, score on the one left out, and repeat until every fold has been left out once. Then we average the k scores.*
   ▸ five rows of five blocks, a different block held out in each row
3. **Har bir kuzatuv key minus bir marta oʻqitishda va bir marta baholashda qatnashadi. Hech narsa isrof boʻlmaydi, va bitta emas, key ta baho olamiz — javob qanchalik tebranishini koʻramiz.**
   *Every observation is used k minus one times for training and once for scoring. Nothing is wasted, and we get k scores instead of one, so we see how much the answer wobbles.*
4. **Narxi — oddiy arifmetika: modelni bir marta emas, key marta oʻqitamiz. Key beshga teng boʻlsa, bu odatda arzon. Bir hafta oʻqitiladigan modelda esa unchalik emas.**
   *The cost is plain arithmetic: we train the model k times instead of once. With k equal to five that is usually cheap. For a model that takes a week to train, not so much.*
5. **Yigirma kunimizni aralashtirib, toʻrt kunlik beshta boʻlakka boʻlamiz va uchinchi darajali egri chiziqni besh marta oʻtkazamiz.**
   *We shuffle our twenty days, cut them into five folds of four days, and fit the degree-three curve five times.*
6. **Chetda qolgan boʻlakdagi xatolar: ikki butun oʻndan olti, bir butun yuzdan ellik yetti, ikki butun yuzdan oʻn toʻqqiz, ikki butun yuzdan ellik sakkiz va uch butun yuzdan oltmish olti.**
   *The errors on the fold left out: two point six, one point five seven, two point one nine, two point five eight and three point six six.*
   ▸ the table: fold 1–5, error 2.60, 1.57, 2.19, 2.58, 3.66
7. **Oʻrtachasi ikki butun yuzdan ellik ikki, standart chetlanishi nol butun yuzdan yetmish olti. Asosiy gap — tarqoqlikda. Faqat ikkinchi boʻlakni chetda qoldirganimizda bir butun yuzdan ellik yetti, faqat beshinchisini qoldirganimizda esa uch butun yuzdan oltmish olti degan boʻlardik. Ikkalasi ham qaysi kun qayerga tushganining tasodifi.**
   *The mean is two point five two, the standard deviation zero point seven six. The spread is the point. Holding out only fold two, we would have reported one point five seven; holding out only fold five, three point six six. Either is an accident of which days landed where.*
8. **Kross-validatsiya ikkinchi boʻlimdagi muammoni ham hal qiladi. Har bir darajani xuddi shu beshta boʻlakda baholasak, eng kichik oʻrtacha xato yana uchinchi darajada chiqadi — ikki butun yuzdan ellik ikki. Oʻninchi darajada esa sakkiz butun yuzdan oʻn sakkiz. Darajani faqat oʻqitish kunlari bilan tanladik, test toʻplamiga qoʻl tegizmadik.**
   *Cross-validation also solves section two's problem. Scoring every degree on the same five folds, the smallest mean error again comes out at degree three, two point five two, and degree ten gets eight point one eight. We chose the degree from the training days alone, without touching the test set.*
   ▸ cross-validated error against degree 1–10, its minimum at 3
9. **Endi test toʻplami halol: uni bir marta ochamiz va ikki butun yuzdan oltmish beshni aytamiz.**
   *Now the test set is honest: we open it once and report two point six five.*
10. **Sunʼiy intellektda giperparametrlar — oʻrganish tezligi, daraxt chuqurligi, jarima kuchi — aynan shunday tanlanadi: har bir nomzod kross-validatsiyada baholanadi, gʻolib esa oxirida test toʻplamida bir marta oʻlchanadi.**
    *In AI, hyperparameters, the learning rate, the depth of a tree, the strength of a penalty, are chosen exactly this way: each candidate is scored by cross-validation, and the winner is measured once on the test set at the end.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beshta boʻlakdagi xatolarning oʻrtachasi qancha?**
    *Let's try it ourselves. Pause the video. What is the mean of the five folds' errors?*
12. **Yigʻindisi oʻn ikki butun oʻndan olti. Beshga boʻlamiz: ikki butun yuzdan ellik ikki.**
    *Their sum is twelve point six. Divided by five: two point five two.*
13. **Test xatosi ham bitta son. Unga qanchalik ishonamiz? Keyingi boʻlimda.**
    *The test error is one number too. How far can we trust it? The next section.*

### 6-boʻlim · Section 6 — Koʻrsatkich atrofidagi oraliq · An interval on a metric
1. **Test xatosi yangi berilganlarning tanlanmasidan hisoblanadi. Demak, beshinchi maʼruza bu yerda ham ishlaydi: u ham tasodifiy miqdor, uning ham standart xatosi bor.**
   *A test error is computed from a sample of fresh data. So Lecture 5 applies here too: it is a random variable, and it has a standard error.*
2. **Muammo shundaki, sigmani en ning ildiziga boʻlish formulasi oʻrtacha uchun. Mediana yoki bizning xatomiz kabi koʻrsatkichlar esa oʻrtacha emas, ularning oddiy formulasi yoʻq.**
   *The trouble is that sigma over the square root of n is a formula for a mean. Metrics like a median, or our error, are not means and have no tidy formula.*
3. **Butstrep usuli: test toʻplamidan xuddi shuncha oʻlchamdagi yangi tanlanmani qaytarib tanlash bilan olamiz, koʻrsatkichni qayta hisoblaymiz va buni minglab marta takrorlaymiz. Shu qiymatlarning tarqoqligi koʻrsatkichning tarqoqligini baholaydi.**
   *The bootstrap: we draw a new sample of the same size from the test set, with replacement, recompute the metric, and repeat thousands of times. The spread of those values estimates the spread of the metric.*
4. **«Qaytarib tanlash» degani: bir kunni olgach, uni qaytadan qutiga solamiz. Ikkinchi maʼruzada paypoqlarni qaytarmasdan olgan edik, bu yerda esa qaytaramiz. Shuning uchun bir kun ikki marta chiqishi, boshqasi umuman chiqmasligi mumkin. Bizning qayta tanlanmalarimizda qirq kundan oʻrtacha oʻn toʻrt yarimtasi tushib qoldi.**
   *"With replacement" means that after we draw a day, we put it back in the box. In Lecture 2 we drew socks without replacement; here we put them back. So one day can come up twice and another not at all. In our resamples, on average fourteen and a half of the forty days were left out.*
   ▸ forty day tiles; one resample: some tiles ×2, some greyed out
5. **Nega bu ishlaydi? Test toʻplami — bosh toʻplamning eng yaxshi oʻrinbosari. Undan qayta tanlash yangi test toʻplamini olishga taqlid qiladi — biz qila olmaydigan ishga.**
   *Why does it work? The test set is our best stand-in for the population. Drawing from it imitates drawing a fresh test set, the thing we cannot afford.*
6. **Uchinchi daraja qirq test kunida ikki butun yuzdan oltmish besh stakan xato qildi. Bu qirq kunni oʻn ming marta qayta tanlaymiz.**
   *Degree three scored an error of two point six five cups on the forty test days. We resample those forty days ten thousand times.*
7. **Qayta tanlangan xatolarning oʻrtadagi toʻqson besh foizi ikki butun yuzdan uchdan uch butun yuzdan yigirma toʻrtgacha: oraliq bir stakandan ham keng.**
   *The middle ninety-five percent of the resampled errors runs from two point zero three to three point two four: an interval more than a cup wide.*
   ▸ the bootstrap histogram, the measured 2.65 line and the 95 % lines at 2.03 and 3.24
8. **Boshqa tomondan tekshiraylik. Qayta tanlangan xatolarning standart chetlanishi nol butun yuzdan oʻttiz bir. Toʻrtinchi maʼruzadagi ikki sigma qoidasi bilan ikki butun yuzdan oltmish besh, plyus-minus ikki standart chetlanish: ikki butun yuzdan uchdan uch butun yuzdan yigirma oltigacha. Deyarli oʻsha oraliq.**
   *Let's check it from another side. The resampled errors have a standard deviation of zero point three one. With Lecture 4's two-sigma rule, two point six five plus or minus two standard deviations runs from two point zero three to three point two six. Almost the same interval.*
9. **Demak, «xato ikki butun yuzdan oltmish besh» degani aslida «xato taxminan ikki bilan uch butun oʻndan ikki orasida, qirq kun esa aniqroq aytishga yetmaydi». Ikki butun oʻndan olti xato qilgan raqib model bu modeldan yaxshiroq emas: oraliqlari deyarli toʻliq ustma-ust.**
   *So "the error is two point six five" really means "the error is somewhere around two to three point two, and forty days is not enough to say better". A rival model with an error of two point six has not beaten this one: their intervals overlap almost entirely.*
10. **Aniqlik bilan ham shunday. Uchinchi maʼruzada toʻqson foiz aniqlikdagi model yuzta test misolida oʻrtacha toʻqsonta toʻgʻri javob berishini, standart chetlanish esa uchta javob ekanini koʻrgan edik.**
    *It is the same with accuracy. In Lecture 3 we saw that a model with ninety percent accuracy gets ninety of a hundred test examples right on average, with a standard deviation of three answers.*
11. **Ming misollik test toʻplamida toʻqson foizli aniqlikning standart xatosi — nol butun toʻqqizni nol butun birga koʻpaytirib, mingga boʻlib, ildizdan chiqarganimiz: nol butun oʻn mingdan toʻqson besh. Toʻqson besh foizli oraliq — taxminan plyus-minus bir butun oʻndan toʻqqiz foiz punkt.**
    *On a test set of a thousand examples, the standard error of ninety percent accuracy is zero point nine times zero point one, over a thousand, square-rooted: zero point zero zero nine five. The ninety-five percent interval is roughly plus or minus one point nine percentage points.*
    ▸ SE = √(0.9 × 0.1 / 1000) = 0.0095; 90 % ± 1.9
12. **Demak, toʻqson foizga qarshi toʻqson butun oʻndan uch foiz — natija emas. Oraliqlar deyarli ustma-ust, va test toʻplamini boshqacha ajratsak, gʻolib almashib qolishi ham mumkin.**
    *So ninety percent against ninety point three percent is not a result. The intervals sit almost on top of each other, and a different test split could easily swap the winner.*
13. **Beshinchi maʼruzadagi en ning ildizi bu yerda ham hukmron: noaniqlikni ikki baravar kamaytirish uchun toʻrt baravar koʻp test berilganlari kerak. Oʻn ming misolda oraliq plyus-minus nol butun oʻndan olti punkt — faqat shunda nol butun oʻndan uch foiz haqida bahslashsa boʻladi.**
    *Lecture 5's square root of n rules here too: halving the uncertainty needs four times the test data. At ten thousand examples the interval is plus or minus zero point six points, and only then is zero point three percent worth arguing about.*
14. **Sunʼiy intellektda reyting jadvallari, maqolalar va yangi versiya eʼlonlari bitta aniqlik sonini yozadi. Bu son — baho, va uning standart xatosi bor, kimdir uni yozsa ham, yozmasa ham.**
    *In AI, leaderboards, papers and release notes report a single accuracy. That number is an estimate, and it has a standard error whether or not anyone prints it.*
15. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Test toʻplami toʻrt ming misol boʻlsa, toʻqson foizli aniqlik atrofidagi toʻqson besh foizli oraliq qancha boʻladi?**
    *Let's try it ourselves. Pause the video. With a test set of four thousand examples, how wide is the ninety-five percent interval around ninety percent accuracy?*
16. **Toʻrt baravar koʻp berilganlar — oraliq ikki baravar tor: taxminan plyus-minus nol butun oʻndan toʻqqiz punkt.**
    *Four times the data, half the interval: about plus or minus zero point nine points.*
17. **Mana shu bilan nolinchi qismni tugatamiz. Lekin ikki model har xil natija bersa, bu farq haqiqiymi yoki tasodifmi? Birinchi qismda.**
    *That completes part zero. But when two models score differently, is the difference real or chance? In part one.*

## Part 1 — Gipotezalarni tekshirish va kalibrlash
▸ part card "1-qism · Gipotezalarni tekshirish va kalibrlash"

### 7-boʻlim · Section 7 — Nol gipoteza va pi-qiymat · The null hypothesis and the p-value
1. **Ikki model yoki ikki usul har doim biroz har xil natija beradi. Shuning uchun savol «qaysi biri oldinda?» emas, balki «u tasodif ham bera oladigan farqdan koʻproq oldindami?»**
   *Two models or two methods always score a little differently. So the question is never "which one is ahead?" but "is it ahead by more than chance alone would produce?"*
2. **Qahvaxona ikki xil menyu chop etdi. Ey menyusini koʻrgan oltmish mijozdan yigirma bittasi pishiriq oldi — oʻttiz besh foiz. Bi menyusini koʻrgan oltmishtadan oʻttiztasi oldi — ellik foiz.**
   *The coffee shop printed two menu layouts. Of sixty customers shown menu A, twenty-one bought a pastry: thirty-five percent. Of sixty shown menu B, thirty bought: fifty percent.*
   ▸ two menus; 21 of 60 and 30 of 60 as dot grids
3. **Oʻn besh foiz punkt juda katta farqdek koʻrinadi. Lekin menyular aynan bir xil boʻlganda, bir yuz yigirma mijozni tasodifan ikki guruhga boʻlsak, bunday farq qanchalik tez-tez chiqardi?**
   *Fifteen percentage points looks decisive. But if the menus were identical and we split a hundred and twenty customers into two groups at random, how often would a gap that big turn up?*
4. **Bu savolning javobi — bitta son, va u pi-qiymat deb ataladi. Usiz «bi yaxshiroq» degan gap bitta tushdan keyingi vaqtning tavsifi, xulosa emas.**
   *The answer to that question is one number, and it is called the p-value. Without it, "B is better" describes one afternoon; it is not a finding.*
5. **Nol gipoteza — zerikarli tushuntirish: hech narsa boʻlmayapti, koʻrganimiz oddiy tebranish. Bu yerda: ikki menyuda xarid ulushi bir xil, qaysi mijoz qaysi menyuni koʻrgani ahamiyatsiz.**
   *The null hypothesis is the boring explanation: nothing is going on, and what we saw is ordinary variation. Here: both menus have the same buying share, and which customer saw which menu did not matter.*
6. **Muqobil gipoteza — dalil kerak boʻlgan narsa: menyular haqiqatan farq qiladi.**
   *The alternative hypothesis is what we would need evidence for: the menus really differ.*
7. **Pi-qiymat — nol gipoteza toʻgʻri boʻlganda, bizniki kabi yoki undan ham keskinroq natija koʻrish ehtimoli. Bu yerda: menyular bir xil boʻlsa, farq qanchalik tez-tez oʻn besh punktga yetadi?**
   *The p-value is the probability of a result at least as extreme as ours if the null hypothesis were true. Here: if the menus were identical, how often would the gap reach fifteen points?*
   ▸ H₀, H₁ and p-qiymat, each with its menu reading
8. **Ikkinchi maʼruzadagi shartli ehtimollikni eslaylik: pi-qiymat — nol gipoteza sharti ostidagi ehtimollik. Biz «agar menyular bir xil boʻlsa» deb faraz qilamiz va shu dunyoda natijamiz qanchalik gʻayrioddiy ekanini soʻraymiz.**
   *Recall conditional probability from Lecture 2: the p-value is a probability given the null hypothesis. We assume "if the menus were the same" and ask how unusual our result is in that world.*
   ▸ p = P(natija kamida shunchalik keskin | H₀)
9. **Kichik pi-qiymat — zerikarli tushuntirish koʻrganimizni zoʻrgʻa beradi degani. U farq qanchalik kattaligini ham, muhimligini ham aytmaydi.**
   *A small p-value means the boring explanation struggles to produce what we saw. It says neither how big the difference is nor whether it matters.*
10. **Sunʼiy intellektda kompaniyalar yangi tavsiya modelini shunday sinaydi: foydalanuvchilarning bir qismiga eski modelni, boshqasiga yangisini koʻrsatadi va farq tasodifdan kattami, deb tekshiradi. Bu ey-bi test deb ataladi.**
    *In AI, companies test a new recommender this way: they show some users the old model and others the new one, and check whether the difference is bigger than chance. That is called an A/B test.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Nol gipoteza toʻgʻri boʻlsa, ikkala menyu uchun umumiy xarid ulushining bahosi qancha?**
    *Let's try it ourselves. Pause the video. If the null hypothesis is true, what is our estimate of the buying share common to both menus?*
12. **Ikki menyuni birlashtiramiz: bir yuz yigirma mijozdan ellik bittasi pishiriq oldi. Ellik birni bir yuz yigirmaga boʻlamiz: qirq ikki yarim foiz.**
    *We pool the two menus: fifty-one of a hundred and twenty customers bought a pastry. Fifty-one divided by a hundred and twenty: forty-two and a half percent.*
13. **Tasodif qanday farqlar berishini formulasiz qanday bilamiz? Keyingi boʻlimda.**
    *How do we find out, without a formula, what gaps chance produces? The next section.*

### 8-boʻlim · Section 8 — Permutatsiya testi · The permutation test
1. **Gʻoya: menyu hech qanday farq qilmasa, har bir mijoz qaysi menyuni koʻrishidan qatʼi nazar pishiriqni baribir olardi yoki olmasdi. Unda menyu nomlarini mijozlar orasida almashtirib qoʻysa ham boʻladi.**
   *The idea: if the menu made no difference, each customer would have bought a pastry or not, whichever menu they saw. Then the menu names could be swapped between customers freely.*
2. **Shuning uchun bir yuz yigirma mijozni birlashtiramiz, menyu nomlarini aralashtiramiz, oltmishtadan ikki guruhga boʻlamiz va farqni qayta hisoblaymiz. Bu — «faqat tasodif nima beradi» degan taqsimotdan bitta qiymat.**
   *So we pool all hundred and twenty customers, shuffle the menu names, split them into two groups of sixty, and recompute the gap. That is one draw from "what chance alone produces".*
   ▸ 120 cards (51 filled), shuffled into two rows of 60, the gap computed
3. **Buni minglab marta takrorlaymiz. Aralashtirilgan farqlar gistogrammasi — nol gipoteza ostidagi taqsimotning oʻzi. Biz uni faraz qilmadik, qurdik.**
   *We repeat it thousands of times. The histogram of shuffled gaps is the distribution under the null hypothesis itself. We did not assume it; we built it.*
4. **Buni nega bilish kerak? Unga solishtirilayotgan narsaning formulasi kerak emas. Xarid ulushi oʻrniga mediana yoki istalgan model koʻrsatkichini qoʻysak ham, xuddi shu aralashtirish oʻzgarishsiz ishlaydi.**
   *Why is it worth knowing? It needs no formula for the thing being compared. Put a median or any model metric in place of the buying share, and the same shuffle works unchanged.*
5. **Oʻsha bir yuz yigirma mijozni yigirma ming marta aralashtirdik. Bizning nol butun yuzdan oʻn besh farqimiz kulrang gistogrammaning ichida, undan tashqarida emas.**
   *We shuffled the same hundred and twenty customers twenty thousand times. Our gap of zero point one five sits inside the grey histogram, not beyond it.*
6. **Shunday katta farq yigirma ming aralashtirishning ikki ming yetti yuz ellik oltitasida chiqdi — oʻn uch butun oʻndan sakkiz foiz. Demak, pi-qiymat nol butun yuzdan oʻn toʻrt.**
   *A gap that big turned up in two thousand seven hundred and fifty-six of the twenty thousand shuffles: thirteen point eight percent. So the p-value is zero point one four.*
   ▸ the permutation histogram, both tails at ±0.15 in orange, "13.8 %"
7. **Boshqa tomondan qaraylik. Aralashtirilgan farqlarning standart chetlanishi taxminan nol butun yuzdan toʻqqiz — bu farqning standart xatosi. Bizning oʻn besh punktimiz bor-yoʻgʻi bir butun oʻndan yetti standart xato. Toʻrtinchi maʼruzadagi qoidaga koʻra, ikki standart chetlanishdan tashqarisi atigi besh foiz hollarda uchraydi. Bizning farqimiz bu chegaraga yetmadi.**
   *Look at it from another side. The shuffled gaps have a standard deviation of about zero point zero nine: that is the gap's standard error. Our fifteen points are only one point seven standard errors. By Lecture 4's rule, beyond two standard deviations happens only five percent of the time. Our gap did not reach that line.*
8. **Oʻqiymiz: oltmishtadan mijozda oʻttiz besh foizga qarshi ellik foiz — aynan bir xil ikki menyu taxminan har yettinchi tushdan keyin beradigan natija.**
   *Read it: thirty-five against fifty percent on sixty customers each is what an identical pair of menus produces about one afternoon in seven.*
9. **Nima hal qilardi? Xuddi shu farq har menyuda taxminan toʻqson mijozda chiqsa, pi-qiymat nol butun yuzdan beshdan kichik boʻladi. Farq oʻzgarmadi — dalil oʻzgardi.**
   *What would settle it? The same gap on about ninety customers per menu would bring the p-value under zero point zero five. The effect did not change; the evidence did.*
10. **Endi pi-qiymat nima emasligini aytaylik. Pi nol butun yuzdan oʻn toʻrt — menyular bir xil boʻlishining ehtimoli oʻn toʻrt foiz degani emas. Pi-qiymat nol gipotezani faraz qilib hisoblanadi: bu nol gipoteza sharti ostida berilganlarning ehtimoli, berilganlar sharti ostida nol gipotezaning ehtimoli emas. Ikkinchi maʼruzada bularni almashtirishni prokuror xatosi degan edik.**
    *Now let's say what a p-value is not. P equal to zero point one four does not mean a fourteen percent chance that the menus are the same. The p-value is computed assuming the null hypothesis: it is the probability of the data given the null, not of the null given the data. In Lecture 2 we called swapping those two the prosecutor's fallacy.*
    ▸ P(berilganlar | H₀) ≠ P(H₀ | berilganlar)
11. **Katta pi-qiymat effekt yoʻqligining isboti emas. U faqat bu berilganlar menyularni ajrata olmaganini aytadi. Dalil yoʻqligi — yoʻqlik dalili emas.**
    *A large p-value is not proof of no effect. It only says this data could not tell the menus apart. Absence of evidence is not evidence of absence.*
12. **Kichik pi-qiymat ham katta effekt degani emas. Har menyuda ikki yuz ming mijoz boʻlsa, nol butun oʻndan toʻrt punktlik farq ham pi-qiymatni taxminan nol butun yuzdan birga tushiradi: statistik jihatdan ishonchli, tijorat uchun esa ahamiyatsiz.**
    *Nor is a small p-value a big effect. With two hundred thousand customers per menu, even a gap of zero point four points brings the p-value down to about zero point zero one: statistically convincing and commercially pointless.*
13. **Nol butun yuzdan besh — tabiat qonuni emas, kelishuv. Pi nol butun mingdan qirq toʻqqiz bilan nol butun mingdan ellik bir orasida dunyoda hech narsa oʻzgarmaydi.**
    *Zero point zero five is a convention, not a law of nature. Nothing about the world changes between p equal to zero point zero four nine and zero point zero five one.*
14. **Sunʼiy intellektda ikki modelni bir xil test toʻplamida solishtirganda ham shu aralashtirish ishlaydi: har bir misolda ikki modelning javoblarini tasodifan almashtiramiz va farqni qayta hisoblaymiz. Koʻrsatkich qanchalik murakkab boʻlmasin, formula kerak emas.**
    *In AI, the same shuffle works when two models are compared on one test set: on each example we swap the two models' answers at random and recompute the gap. However complex the metric, no formula is needed.*
15. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oltmishtadan mijozda farq taxminan bir butun oʻndan yetti standart xato edi. Har menyuda toʻqson mijoz boʻlsa, standart xato necha baravar kichrayadi va farq ikki standart xatodan oshadimi?**
    *Let's try it ourselves. Pause the video. With sixty customers each, the gap was about one point seven standard errors. With ninety customers per menu, by how many times does the standard error shrink, and does the gap pass two standard errors?*
16. **Beshinchi maʼruzadagi qoida: standart xato en ning ildiziga teskari kamayadi. Toʻqsonni oltmishga boʻlsak, bir yarim, uning ildizi taxminan bir butun yuzdan yigirma ikki. Farq taxminan ikki butun yuzdan toʻrt standart xatoga oʻsadi — ikki chegarasidan oshdi.**
    *Lecture 5's rule: the standard error shrinks with the square root of n. Ninety over sixty is one and a half, and its square root is about one point two two. The gap grows to about two point zero four standard errors: past the line at two.*
17. **Test asosida qaror qilsak, qanday xato qilishimiz mumkin? Keyingi boʻlimda.**
    *When we decide from a test, how can we be wrong? The next section.*

### 9-boʻlim · Section 9 — Birinchi va ikkinchi tur xatolar · Type I and Type II errors
1. **Test asosida qaror qilsak, ikki xil xato qilishimiz mumkin, va ular bir-biriga qarshi ishlaydi.**
   *When we decide from a test, there are two ways to be wrong, and they pull against each other.*
2. **Nol gipoteza toʻgʻri, biz esa uni rad etsak — bu birinchi tur xato, yaʼni yolgʻon signal. Nol gipoteza notoʻgʻri, biz esa uni rad etmasak — bu ikkinchi tur xato, yaʼni farqni oʻtkazib yubordik.**
   *If the null hypothesis is true and we reject it, that is a Type I error, a false alarm. If the null hypothesis is false and we do not reject it, that is a Type II error: we missed the difference.*
   ▸ the 2×2 table: rad etamiz / rad etmaymiz × H₀ toʻgʻri / H₀ notoʻgʻri
3. **Bu ikkinchi maʼruzadagi tibbiy test jadvalining oʻzi, faqat yangi nomlar bilan. Birinchi tur xato — yolgʻon musbat, ikkinchi tur xato — yolgʻon manfiy. Oʻn ming kishidan toʻrt yuz toʻqson besh sogʻlom kishini kasal deb topgan test toʻrt yuz toʻqson beshta birinchi tur xato qilgan edi.**
   *This is Lecture 2's medical-test table under new names. A Type I error is a false positive; a Type II error is a false negative. The test that found four hundred and ninety-five healthy people of ten thousand ill made four hundred and ninety-five Type I errors.*
   ▸ Lecture 2's screening table beside the new one, the 495 cell lit
4. **Chegara bu muvozanatni boshqaradi. Nol butun yuzdan besh oʻrniga nol butun yuzdan birni talab qilsak, yolgʻon signallar kamayadi, oʻtkazib yuborilgan farqlar esa koʻpayadi.**
   *The threshold controls the trade. Demanding zero point zero one instead of zero point zero five makes false alarms rarer and misses more common.*
5. **Asosiy ulush bu yerda ham hukmron. Tibbiy testda besh yuz toʻqson besh musbat natijaning toʻrt yuz toʻqson beshtasi, yaʼni sakson uch foizi yolgʻon signal edi, chunki kasallar juda kam edi. Sinayotgan gʻoyalarimizning koʻpi foydasiz boʻlsa, «ahamiyatli» natijalarimizning koʻpi ham yolgʻon signal boʻladi.**
   *The base rate still rules. In the medical test, four hundred and ninety-five of the five hundred and ninety-five positives, eighty-three percent, were false alarms, because so few people were ill. If most of the ideas we test are duds, most of our "significant" results will be false alarms too.*
6. **Endi koʻp test. Modelni sozlash — koʻp konfiguratsiyani sinab koʻrish va validatsiyada eng yaxshisini qoldirish. Har bir solishtirish — bitta test, va har bir test oʻzining yolgʻon signal ehtimoliga ega.**
   *Now many tests. Tuning a model means trying many configurations and keeping the best on validation data. Every comparison is a test, and every test has its own chance of a false alarm.*
7. **Besh foizli chegarada em ta mustaqil testdan kamida bittasida yolgʻon signal chiqish ehtimoli — birdan nol butun yuzdan toʻqson beshning em darajasini ayirganimiz. Bu birinchi maʼruzadagi «kamida bitta» hisobi: avval «hech qaysisida», keyin birdan ayiramiz.**
   *At a five percent threshold, the chance of at least one false alarm across m independent tests is one minus zero point nine five to the power m. It is Lecture 1's "at least one" calculation: first "none at all", then subtract from one.*
   ▸ 1 − 0.95^m
8. **Bitta testda — nol butun yuzdan besh. Oʻnta testda — nol butun oʻndan toʻrt. Yigirmatada — nol butun yuzdan oltmish toʻrt. Elliktada — nol butun yuzdan toʻqson ikki.**
   *With one test, zero point zero five. With ten, zero point four. With twenty, zero point six four. With fifty, zero point nine two.*
   ▸ the table: m = 1, 10, 20, 50 → 0.05, 0.40, 0.64, 0.92
9. **Boshqacha aytsak: ellikta testda oʻrtacha ikki yarimta yolgʻon signal kutamiz. Ellikta giperparametr sozlamasini sinasak, validatsiyada nimadir deyarli har doim ajoyib koʻrinadi.**
   *Put another way: across fifty tests we expect two and a half false alarms on average. Try fifty hyperparameter settings and something will look brilliant on validation data almost every time.*
10. **Shuning uchun koʻp validatsiya baholarining eng yaxshisi yuqoriga tarafkash. Gʻolibni qoʻl tegizilmagan test toʻplamida qayta oʻlchash kerak. Uchta toʻplamga ajratishning haqiqiy sababi — shu.**
    *That is why the best of many validation scores is biased upwards, and the winner must be measured again on the untouched test set. This is the real reason for the three-way split.*
11. **Sunʼiy intellektda bir kunda yuzlab tajriba oʻtkazadigan jamoalarda bu juda muhim: eng yaxshi koʻringan natija shunchaki eng omadlisi boʻlishi mumkin.**
    *In AI this matters a great deal for teams that run hundreds of experiments a day: the best-looking result may simply be the luckiest.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻnta mustaqil testda kamida bitta yolgʻon signal chiqish ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. Across ten independent tests, what is the chance of at least one false alarm?*
13. **Nol butun yuzdan toʻqson beshning oʻninchi darajasi taxminan nol butun oʻndan olti. Birdan ayiramiz: nol butun oʻndan toʻrt.**
    *Zero point nine five to the tenth power is about zero point six. Subtracting from one: zero point four.*
14. **Model faqat javob emas, ehtimol ham bersa-chi? Bu ehtimolga ishonsa boʻladimi? Keyingi boʻlimda.**
    *What if a model gives not just an answer but a probability? Can that probability be trusted? The next section.*

### 10-boʻlim · Section 10 — Kalibrlash · Calibration
1. **Eng foydali bashoratlar — javob emas, ehtimol: «ertaga yomgʻir yogʻish ehtimoli yetmish foiz», «bu mushuk ekaniga toʻqson foiz ishonaman». Aniqlik faqat javobni baholaydi, unga qoʻshilgan sonni esa eʼtiborsiz qoldiradi.**
   *The most useful predictions are not an answer but a probability: "seventy percent chance of rain tomorrow", "ninety percent sure this is a cat". Accuracy grades only the answer and ignores the number attached to it.*
2. **Ikki sinoptik bir xil yuz kunda «yomgʻir ehtimoli yetmish foiz» deydi. Birinchisida yuz kundan yetmishtasida yomgʻir yogʻadi, ikkinchisida — qirq beshtasida. Ikkalasi ham yomgʻirli kunlarda «toʻgʻri» edi. Lekin «yetmish foiz» deganda faqat birinchisi biror narsani nazarda tutgan.**
   *Two forecasters both say "seventy percent chance of rain" on the same hundred days. For the first it rains on seventy of them, for the second on forty-five. Both were "right" on the rainy days. But only the first meant anything by seventy percent.*
   ▸ two rows of 100 day squares, 70 and 45 rainy
3. **Bashorat kalibrlangan deymiz, agar aytilgan ehtimol kuzatilgan chastotaga mos kelsa: yetmish foiz deb aytilgan kunlarning taxminan yetmish foizida yomgʻir yogʻishi kerak.**
   *We call a forecast calibrated when the stated probability matches the observed frequency: on about seventy percent of the days labelled seventy percent, it should rain.*
4. **Bu birinchi maʼruzadagi ehtimollikning oʻzi — uzoq muddatdagi ulush. Kalibrlash shuni tekshiradi: model aytgan ehtimol uzoq muddatda haqiqatan shunday ulushga aylanadimi?**
   *This is Lecture 1's probability itself: a long-run share. Calibration checks exactly that: does the probability the model states really become that share in the long run?*
5. **Buni bashorat qanday qilinganini bilmasdan tekshirsa boʻladi: bashoratlarni aytilgan ehtimol boʻyicha guruhlaymiz va nima boʻlganini sanaymiz.**
   *This can be checked without knowing how the forecast was made: we group the predictions by the probability stated and count what happened.*
6. **Har bir aytilgan darajada toʻrt yuztadan bashorat: aytilgani va boʻlgani. Mukammal kalibrlash — diagonal chiziq.**
   *Four hundred predictions at each stated level: what was said against what happened. Perfect calibration is the diagonal.*
   ▸ reliability diagram: the diagonal first, then the two forecasters' points
7. **Halol sinoptik: nol butun yuzdan toʻqson besh deganida, voqea nol butun mingdan toʻqqiz yuz ellik sakkiz hollarda roʻy berdi. Oʻrtacha farq — nol butun yuzdan bir.**
   *The honest forecaster: when they said zero point nine five, it happened zero point nine five eight of the time. The average gap is zero point zero one.*
8. **Oʻziga ortiqcha ishongan sinoptik: nol butun yuzdan toʻqson besh deganida, voqea atigi nol butun yuzdan yetmish olti hollarda roʻy beradi, nol butun yuzdan besh deganida esa baribir nol butun yuzdan yigirma ikki hollarda roʻy beradi. Oʻrtacha farq — nol butun yuzdan oʻn ikki.**
   *The overconfident forecaster: a stated zero point nine five happens only zero point seven six of the time, and a stated zero point zero five still happens zero point two two of the time. The average gap is zero point one two.*
9. **Sanab koʻraylik. Toʻqson besh foiz deyilgan toʻrt yuzta bashoratda voqea uch yuz saksontasida roʻy berishi, yigirmatasida roʻy bermasligi kerak edi. Halol sinoptikda u uch yuz sakson uchtasida roʻy berdi. Oʻziga ishongan sinoptikda esa uch yuz beshtasida: yigirmata emas, toʻqson beshta xato.**
   *Let's count it. Of four hundred predictions stated at ninety-five percent, the event should have happened on three hundred and eighty and failed on twenty. For the honest forecaster it happened on three hundred and eighty-three. For the overconfident one, on three hundred and five: not twenty misses but ninety-five.*
10. **Bu ishonchlilik diagrammasi, oʻrtacha vertikal farq esa kalibrlash xatosi. Ikkala sinoptikning aniqligi bir xil boʻlishi ham mumkin.**
    *This is a reliability diagram, and the average vertical gap is the calibration error. The two forecasters could even have the same accuracy.*
11. **Sunʼiy intellektda klassifikatorning softmaks chiqishi doim ehtimol sifatida oʻqiladi: qachon odamga topshirish, qachon javob bermaslik, bir nechta modelni qanday birlashtirishni hal qilish uchun.**
    *In AI, a classifier's softmax output is read as a probability all the time: to decide when to hand over to a human, when to abstain, how to combine several models.*
12. **Qoida: toʻqson foiz ishongan model toʻqson foiz hollarda toʻgʻri boʻlishi kerak. Zamonaviy neyron tarmoqlar koʻpincha bunday emas: ular bir vaqtning oʻzida ham aniq, ham oʻziga haddan tashqari ishongan — qizil chiziq kabi.**
    *The rule: a model that is ninety percent confident should be right ninety percent of the time. Modern neural networks often are not: they are accurate and badly overconfident at once, like the red curve.*
13. **Buni tuzatish uchun qayta oʻqitish shart emas. Softmaks haroratini sozlaymiz: barcha ballarni validatsiya berilganlarida tanlangan bitta songa boʻlamiz. Uchinchi maʼruzadagi softmaksni eslaylik: ikki sinfning ballari ikki va nol boʻlsa, birinchi sinf ehtimoli nol butun yuzdan sakson sakkiz. Ballarni ikkiga boʻlsak, nol butun yuzdan yetmish uch boʻladi. Butun egri chiziq diagonalga yaqinlashguncha shunday yumshatiladi.**
    *Fixing it needs no retraining. We tune the softmax temperature: we divide all the scores by one number chosen on validation data. Recall the softmax from Lecture 3: if two classes score two and zero, the first class gets a probability of zero point eight eight. Divide the scores by two and it becomes zero point seven three. The whole curve is softened this way until it sits near the diagonal.*
    ▸ softmax(2, 0) → 0.88; softmax(2/2, 0/2) → 0.73; the red curve easing towards the diagonal
14. **Qayerda muhim? Ishonch chegarasiga qarab harakat qiladigan har qanday tizimda. Oʻziga ortiqcha ishongan model hech qachon odamga topshirmaydi, chunki u hech qachon ikkilanmaydi.**
    *Where does it bite? In any system that acts on a confidence threshold. An overconfident model never hands over to a human, because it is never in doubt.*
15. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Sinoptik toʻrt yuz kunda «toʻqson besh foiz» dedi. Kalibrlangan boʻlsa, voqea nechta kunda roʻy berishi kerak? Oʻziga ishongan sinoptikda nechtasida roʻy berdi?**
    *Let's try it ourselves. Pause the video. A forecaster said "ninety-five percent" on four hundred days. If calibrated, on how many days should the event happen? For the overconfident forecaster, on how many did it?*
16. **Toʻrt yuz karra nol butun yuzdan toʻqson besh — uch yuz sakson. Oʻziga ishongan sinoptikda — uch yuz besh, yetmish beshta kam.**
    *Four hundred times zero point nine five: three hundred and eighty. For the overconfident forecaster, three hundred and five: seventy-five fewer.*

▸ the module map (still section 10, after the pause): each lecture's idea → the module and lecture that uses it
17. **Keling, butun modulga bir nazar tashlaylik. Bu yerda hech narsa oʻzi uchun oʻrganilmadi: har bir maʼruza keyin ishlatadigan narsamizni chiqardi.**
    *Let's look back over the whole module. Nothing here was learned for its own sake: every lecture derived something we are about to use.*
18. **Ikkinchi maʼruzadagi Bayes formulasi — uchinchi modulning oltinchi maʼruzasidagi matnlar uchun sodda Bayes klassifikatoriga olib boradi. Beshinchi maʼruzadagi maksimal haqiqatga oʻxshashlik — birinchi modulning oʻn uchinchi maʼruzasidagi kross-entropiyaga, klassifikatorning yoʻqotish funksiyasiga.**
    *Lecture 2's Bayes formula leads to Naive Bayes for text in Module 3, Lecture 6. Lecture 5's maximum likelihood leads to cross-entropy, a classifier's loss, in Module 1, Lecture 13.*
19. **Oltinchi maʼruzadagi maksimal aposterior baho — birinchi modulning oʻn ikkinchi maʼruzasidagi Rij va Lasso regressiyasiga. Yettinchi maʼruzadagi entropiya — birinchi modulning beshinchi maʼruzasida qaror daraxti boʻlinishni qanday tanlashiga.**
    *Lecture 6's MAP estimate leads to Ridge and Lasso regression in Module 1, Lecture 12. Lecture 7's entropy leads to how a decision tree chooses a split, in Module 1, Lecture 5.*
20. **Toʻqqizinchi maʼruzadagi kovariatsiya va uning xos vektorlari — birinchi modulning ikkinchi maʼruzasidagi bosh komponentalar tahliliga. Bugungi mavzu esa — birinchi modulning oʻn toʻrtinchi maʼruzasidagi klassifikatorlarni baholash, kross-validatsiya va giperparametrlarni qidirishga.**
    *Lecture 9's covariance and its eigenvectors lead to principal component analysis in Module 1, Lecture 2. And today's topic leads to evaluating classifiers, cross-validation and hyperparameter search in Module 1, Lecture 14.*
21. **Keling, maʼruzani yakunlaylik. Oʻqitish xatosi mehnatni oʻlchaydi, sifatni emas. Sifatni faqat model koʻrmagan berilganlar baholaydi, test toʻplami esa unga qarab tanlagan zahotimiz sarflanadi.**
    *Let's wrap up the lecture. Training error measures effort, not quality. Only data the model has not seen estimates quality, and a test set is spent the moment we choose by it.*
22. **Yangi berilganlardagi xato — tarafkashlik kvadrati, dispersiya va shovqin. Oʻqitish xatosi sigʻim bilan doim kamayadi, shuning uchun qachon toʻxtashni hech qachon aytmaydi. Kross-validatsiya kam berilganlarni qayta ishlatadi va baho qanchalik tebranishini koʻrsatadi, butstrep esa formulasi bor-yoʻqligidan qatʼi nazar har qanday koʻrsatkichga oraliq beradi.**
    *Error on new data is bias squared plus variance plus noise. Training error always falls with capacity, so it never tells us when to stop. Cross-validation reuses scarce data and shows how much a score wobbles, and the bootstrap puts an interval on any metric, formula or not.*
23. **Pi-qiymat «faqat tasodif buni qanchalik tez-tez berardi?» degan savolga javob beradi, permutatsiya testi esa unga hech narsani faraz qilmasdan, aralashtirib javob beradi. Aniqlik javobni baholaydi, kalibrlash — ishonchni. Model birida aʼlo, ikkinchisida yaroqsiz boʻlishi mumkin.**
    *A p-value answers "how often would chance alone do this?", and a permutation test answers it by shuffling, assuming nothing. Accuracy grades the answer, calibration grades the confidence. A model can be excellent at one and useless at the other.*
24. **Mana shu bilan oʻninchi maʼruzamizni va statistika modulini tugatamiz. Keyingi modulda klassik mashinali oʻqitishni oʻrganamiz.**
    *That brings our tenth lecture, and the statistics module, to an end. In the next module, we study classical machine learning.*
