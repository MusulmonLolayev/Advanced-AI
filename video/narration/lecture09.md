# Lecture 9 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Korrelyatsiya va regressiya) = sections
1–8, Part 1 (Koʻp oʻlchovli statistika) = sections 9–11. Each section: problem first → concept as the answer → one AI
use → a hands-on pause → the question the next section answers. The running example is the slides' own: Lecture 4's
300 trading days of temperature and iced coffees (the figure script's sample, regenerated from its seed), then total
drinks, Anscombe's quartet from Lecture 1, and a third column, hot drinks.

**Depth from the start** (the instructor's rule after Lecture 4): each idea is explained from more than one side, and
what it needs from Lectures 1–8 is recapped briefly where it is used. The angles: the covariance in Fahrenheit (units
change the number, not the relationship); the four quadrants counted (240 of 300 days give a positive product);
correlation as the average product of z-scores; the slope as r times the ratio of spreads, so a day one standard
deviation warmer sells only 0.77 of a standard deviation more cups; the line through the mean point; residuals average
zero and carry no trace of temperature; R² as a share of squared gaps and as one minus the residual variance over the
total; r = 0.5 explains only a quarter; least squares as Lecture 5's Gaussian likelihood, and Lecture 4's two-sigma
band around the line (95.7 % of days inside); the U-shape split into a cold half (r = −0.68) and a warm half
(r = +0.69) that cancel; Anscombe's sets II–IV read by their residuals, and why set IV's residual plot stays silent;
Simpson's paradox recalled as a confounder; iced and hot drinks lose their −0.66 once temperature is taken out
(0.01); Σv = λv checked by hand; the eigenvalue as the variance of each day's score along v; Fahrenheit moves the
split from 93.2 % to 88.9 %; with three columns one direction holds 84.4 %.

**Rules applied:** berilganlar (data); "we", never "you" (only *Videoni toʻxtating*); Latin letters spoken by their
English names (ar, ey, bi, eks, uay, vi, key); Greek letters keep theirs (lambda, sigma); numbers spelled for the ear,
digits on screen. Screen labels are words only.
**Numbers:** every figure comes from `video/statistics/raw/l09_numbers.json` / `l09_figures.txt`
(`capture_l09.py`, unit-tested in `test_l09.py`). The 300 days, the total drinks and the hot drinks are the figure
script's own, regenerated from its seeds (11, 29, 7).

**Slide numbers that disagree with the data** (slides not edited; the narration uses the computed values):
- *Why Do We Need Correlation?* says the Fahrenheit covariance is **89.3**. That is the rounded 49.6 × 1.8; the data
  gives 49.56 × 1.8 = **89.2**.
- *The Fitted Line and Its Residuals* gives the example day as **22.4 °C, 28 cups, predicted 40.5**. The figure script's
  example day, whose residual is the slide's −12.5, is **25.0 °C, 31.9 cups, predicted 44.4**. No day near 22.4 °C
  sold 28 cups (the nearest sold 26 and 27, residuals −14.5 and −13.8).
- *The Two Principal Directions* says the arrows are drawn 2√λ long and then quotes **12.2 and 3.3**. Those are √λ,
  the standard deviations along v₁ and v₂; the arrows are 24.4 and 6.6 long.
- *Anscombe's Quartet, Revisited* says that in sets III and IV the point carrying the fit "stands out as a single huge
  residual". True for set III (3.24). In set IV the far point (19, 12.5) has a residual of exactly **0**: the line
  passes through it, so the residual plot cannot flag it; only the scatter does. The narration says so.

**Terms to confirm** (new in this lecture):
- regressiya, chiziqli regressiya (regression, linear regression) · eng kichik kvadratlar usuli (ordinary least
  squares)
- burchak koeffitsiyenti (slope, as in school geometry) · ozod had (intercept) · oʻrtacha nuqta (the mean point)
- qoldiq (residual; already in Lecture 5's 10.4) · qoldiqlar grafigi (residual plot)
- determinatsiya koeffitsiyenti, spoken «ar kvadrat» (R²)
- chalkashtiruvchi omil (confounder) · sababiylik (causation) · bashorat / aralashuv (prediction / intervention) ·
  A/B sinov (A/B test)
- korrelyatsiya matritsasi (correlation matrix) · xos vektor / xos qiymat (eigenvector / eigenvalue) · bosh yoʻnalish
  (principal direction; Lecture 4's bosh komponentalar tahlili) · tushuntirilgan dispersiya ulushi (explained variance)
  · proyeksiya (projection) · oʻlchamni kamaytirish (dimensionality reduction) · skalyar koʻpaytma (dot product)
- kosinus oʻxshashlik (cosine similarity) · Selsiy / Farengeyt · Enskomb kvarteti (Anscombe's quartet; Lecture 1 says
  «Frensis Enskomb») · kross-validatsiya (cross-validation) · logistik regressiya · modellarni baholash /
  gipotezalarni tekshirish (model evaluation / hypothesis testing, Lecture 10) · qaror daraxti (decision tree)

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "9-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Toʻqqizinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda korrelyatsiya va regressiyani oʻrganamiz, birinchi qismda esa koʻp oʻlchovli statistika bilan tanishamiz.**
   *Hello, dear friends, and welcome to our ninth lecture. It also has two parts. In part zero we study correlation and regression, and in part one we meet multivariate statistics.*

## Part 0 — Korrelyatsiya va regressiya
▸ part card "0-qism · Korrelyatsiya va regressiya"

### 1-boʻlim · Section 1 — Nega korrelyatsiya kerak · Why we need correlation
1. **Shu paytgacha har safar bitta miqdorni tasvirladik: oʻrtacha qiymat, tarqoqlik, taqsimot. Lekin foydali savollar deyarli doim juftlik haqida: issiq kunlarda muzli qahva koʻproq sotiladimi, koʻproq oʻqisak bahomiz oshadimi?**
   *So far we have described one quantity at a time: a mean, a spread, a distribution. But the useful questions are almost always about a pair: do warm days sell more iced coffee, does studying more raise the mark?*
   ▸ two separate histograms (temperature, cups), then a question mark between them
2. **Toʻrtinchi maʼruzadagi qahvaxonani eslaylik. Uch yuz ish kunida havo harorati va sotilgan muzli qahvalar sonini yozib borgan edik. Kovariatsiya qirq toʻqqiz butun oʻndan olti chiqqan edi — musbat, yaʼni ikkalasi birga oshadi.**
   *Let's recall the coffee shop from Lecture 4. Over three hundred trading days we recorded the temperature and the iced coffees sold. The covariance came out at forty-nine point six: positive, so the two rise together.*
   ▸ the 300 days as a scatter; cov = 49.6
3. **Lekin qirq toʻqqiz butun oʻndan olti nima? Uning birligi — daraja karra stakan. Haroratni Farengeytda yozsak, xuddi oʻsha bogʻlanish sakson toʻqqiz butun oʻndan ikki boʻlib chiqadi.**
   *But forty-nine point six what? Its unit is degrees times cups. Record the temperature in Fahrenheit and the very same relationship comes out as eighty-nine point two.*
   ▸ the temperature axis relabelled °C → °F; 49.6 → 89.2
4. **Bogʻlanish oʻzgarmadi, faqat son oʻzgardi. Kattaligi birlikka bogʻliq boʻlgan son bogʻlanish kuchli yoki kuchsiz ekanini ayta olmaydi.**
   *The relationship did not change; only the number did. A number whose size depends on the units cannot say whether a relationship is strong or weak.*
5. **Yechim: kovariatsiyani ikkala standart chetlanishga boʻlamiz. Birliklar qisqarib ketadi va son har doim minus birdan birgacha boʻladi. Bu korrelyatsiya, uni ar harfi bilan belgilaymiz.**
   *The fix: we divide the covariance by both standard deviations. The units cancel and the number always lands between minus one and one. That is the correlation, written with the letter r.*
   ▸ r = s_xy / (s_x s_y)
6. **Bizning kunlarda: qirq toʻqqiz butun oʻndan oltini besh butun yuzdan oltmish besh karra oʻn bir butun yuzdan oʻttiz uchga boʻlamiz — nol butun yuzdan yetmish yetti. Toʻrtinchi maʼruzada ham aynan shu son chiqqan edi.**
   *For our days: forty-nine point six divided by five point six five times eleven point three three is zero point seven seven. The same number Lecture 4 found.*
   ▸ 49.6 / (5.65 × 11.33) = 0.77
7. **Birinchi maʼruzada aytgandik: ar teng bir — mukammal koʻtariluvchi toʻgʻri chiziq, minus bir — mukammal tushuvchi, nol esa toʻgʻri chiziqli bogʻlanish yoʻq degani. Nol butun yuzdan yetmish yetti — kuchli va musbat bogʻlanish.**
   *As we said in Lecture 1: r equal to one is a perfect rising line, minus one a perfect falling one, and zero means no straight-line relationship. Zero point seven seven is strong and positive.*
   ▸ the −1 … 1 scale with three small sketch scatters (labelled as illustrations) at −1, 0, 1, and 0.77 marked
8. **Sunʼiy intellektda belgilar har xil birlikda boʻladi: yosh — yilda, daromad — dollarda, masofa — kilometrda. Qaysi belgi maqsad bilan kuchliroq bogʻlanganini solishtirish uchun kovariatsiyaga emas, korrelyatsiyaga qaraymiz.**
   *In AI, features come in different units: age in years, income in dollars, distance in kilometres. To compare which feature is more strongly tied to the target, we look at the correlation, not the covariance.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Farengeytda kovariatsiya sakson toʻqqiz butun oʻndan ikki, harorat standart chetlanishi esa bir butun oʻndan sakkiz baravar katta. Korrelyatsiya qancha boʻladi?**
   *Let's try it ourselves. Pause the video. In Fahrenheit the covariance is eighty-nine point two, and the temperature's standard deviation is one point eight times larger. What is the correlation?*
10. **Surat ham, maxraj ham bir butun oʻndan sakkiz baravar oshdi va qisqarib ketdi: yana nol butun yuzdan yetmish yetti. Korrelyatsiya birlikka qaramaydi.**
    *Both the numerator and the denominator grew one point eight times and cancel: zero point seven seven again. The correlation ignores units.*
11. **Kovariatsiya nega musbat chiqadi? Uni nuqtalar bulutida koʻrish mumkinmi? Keyingi boʻlimda.**
    *Why does the covariance come out positive? Can we see it in the cloud of points? The next section.*

### 2-boʻlim · Section 2 — Toʻrt chorak · The four quadrants
1. **Nuqtalar bulutiga oʻrtacha nuqtani qoʻyamiz: yigirma bir butun oʻndan sakkiz daraja va oʻttiz toʻqqiz butun oʻndan besh stakan. Undan oʻtgan ikki chiziq rasmni toʻrt chorakka boʻladi.**
   *We mark the mean point on the cloud: twenty-one point eight degrees and thirty-nine point five cups. The two lines through it cut the picture into four quadrants.*
   ▸ the scatter with a grey crosshair at (21.8, 39.5) and the mean point in red
2. **Issiq va gavjum kun oʻng yuqorida turadi: ikkala farq ham musbat, koʻpaytmasi ham musbat. Salqin va sokin kun chap pastda: ikkala farq ham manfiy, manfiy karra manfiy esa yana musbat.**
   *A warm, busy day sits upper right: both deviations are positive, and so is their product. A cool, quiet day sits lower left: both deviations are negative, and a negative times a negative is positive again.*
   ▸ one upper-right day and one lower-left day, each with its two deviations drawn as arrows and a "+" sign
3. **Qolgan ikki chorakdagi kunlar manfiy koʻpaytma beradi: salqin, lekin gavjum kun yoki issiq, lekin sokin kun.**
   *Days in the other two quadrants give negative products: a cool but busy day, or a warm but quiet one.*
4. **Sanab koʻraylik. Oʻng yuqorida bir yuz oʻn toʻrt kun, chap pastda bir yuz yigirma olti kun: jami ikki yuz qirq kunda koʻpaytma musbat. Qolgan ikki chorakda bor-yoʻgʻi yigirma yetti va oʻttiz uch kun.**
   *Let's count. One hundred fourteen days upper right, one hundred twenty-six lower left: two hundred forty days with a positive product. The other two quadrants hold only twenty-seven and thirty-three days.*
   ▸ the four quadrants lit with their counts: 114, 126, 27, 33
5. **Kovariatsiya — shu koʻpaytmalarning oʻrtachasi. Musbat choraklar yutadi, shuning uchun u musbat.**
   *The covariance is the average of these products. The positive quadrants win, so it is positive.*
6. **Korrelyatsiyaga ham shu yerdan boshqa tomondan qaraymiz. Har bir farqni oʻz standart chetlanishiga boʻlsak, toʻrtinchi maʼruzadagi zed-qiymat chiqadi. Harorat zed-qiymatini savdo zed-qiymatiga koʻpaytirib, oʻrtachasini olsak — yana nol butun yuzdan yetmish yetti. Korrelyatsiya — zed-qiymatlar koʻpaytmasining oʻrtachasi.**
   *From here we can look at the correlation from another side. Divide each deviation by its own standard deviation and we get Lecture 4's z-score. Multiply the temperature's z-score by the sales' z-score and average: zero point seven seven again. The correlation is the average product of z-scores.*
   ▸ both axes rescaled to z-scores; the cloud keeps its shape; mean of z_x · z_y = 0.77
7. **Sunʼiy intellektda ikki vektorning oʻxshashligini kosinus oʻxshashlik bilan oʻlchaymiz. Ikki ustunni markazlab, standartlashtirsak, ularning kosinus oʻxshashligi aynan korrelyatsiyaga teng boʻladi.**
   *In AI we measure how alike two vectors are by cosine similarity. Centre and standardize two columns, and their cosine similarity is exactly the correlation.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻn besh darajali salqin kunda ellik stakan sotildi. Bu kun qaysi chorakda va uning koʻpaytmasi qanday ishorali?**
   *Let's try it ourselves. Pause the video. On a cool fifteen-degree day, fifty cups were sold. Which quadrant is it in, and what sign is its product?*
9. **Harorat oʻrtachadan past — farq manfiy, savdo oʻrtachadan yuqori — farq musbat. Chap yuqori chorak, koʻpaytma manfiy. Bunday kun kovariatsiyani kamaytiradi.**
   *The temperature is below its mean, a negative deviation; sales are above theirs, a positive one. Upper left quadrant, a negative product. A day like this pulls the covariance down.*
   ▸ the day at (15, 50) in the upper-left quadrant, its product −71.6
10. **Nol butun yuzdan yetmish yetti — bogʻlanish kuchli degani. Lekin ertaga uch daraja issiq boʻlsa, nechta stakan koʻproq tayyorlaymiz? Keyingi boʻlimda.**
    *Zero point seven seven says the relationship is strong. But if tomorrow is three degrees warmer, how many more cups do we prepare? The next section.*

### 3-boʻlim · Section 3 — Eng kichik kvadratlar usuli · Ordinary least squares
1. **Korrelyatsiya bogʻlanish qanchalik kuchli ekanini aytadi, lekin qancha ekanini aytmaydi. Uning birligi yoʻq, shuning uchun «nechta stakan» degan savolga javob bera olmaydi.**
   *The correlation says how strong the relationship is, but not how much. It has no units, so it cannot answer "how many cups".*
2. **Toʻgʻri chiziq bunga javob beradi. Uning burchak koeffitsiyenti — tezlik: bir darajaga necha stakan. Yana u hali yozilmagan haroratlarda ham bashorat qiladi.**
   *A line can. Its slope is a rate: cups per degree. And it predicts at temperatures we have never recorded.*
   ▸ ŷ = a + bx drawn through the cloud; b labelled "stakan / daraja"
3. **Qaysi chiziqni olamiz? Har bir kun uchun chiziq bashoratidan haqiqiy savdogacha boʻlgan vertikal farqni olamiz, uni kvadratga koʻtarib, hammasini qoʻshamiz. Shu yigʻindi eng kichik boʻlgan chiziqni tanlaymiz. Bu eng kichik kvadratlar usuli.**
   *Which line do we take? For each day we take the vertical gap from the line's prediction to the real sales, square it, and add them all up. We choose the line whose sum is smallest. That is ordinary least squares.*
   ▸ a few vertical gaps, each turned into a small square; a line swinging until the total area is smallest
4. **Kvadratni birinchi maʼruzadan eslaymiz: dispersiyada ham farqlarni kvadratga koʻtargan edik. Kvadrat ishorani olib tashlaydi va bitta katta xatoni bir nechta kichik xatodan ogʻirroq jazolaydi. Uning asl sababini esa oltinchi boʻlimda koʻramiz.**
   *We remember the square from Lecture 1: we squared the deviations in the variance too. The square removes the sign and punishes one big miss more than several small ones. Its real reason comes in section six.*
5. **Bu masala qidiruvsiz yechiladi, javob tayyor formula. Burchak koeffitsiyenti bi — kovariatsiyani harorat dispersiyasiga boʻlganimiz. Ozod had ey — oʻrtacha savdodan bi karra oʻrtacha haroratni ayirganimiz.**
   *This problem is solved without searching; the answer is a ready formula. The slope b is the covariance divided by the temperature's variance. The intercept a is the mean sales minus b times the mean temperature.*
   ▸ b = s_xy / s_x²,  a = ȳ − b x̄
6. **Ikkinchi formula bitta muhim narsani aytadi: chiziq doim oʻrtacha nuqtadan oʻtadi. Yigirma bir butun oʻndan sakkiz darajada u aynan oʻttiz toʻqqiz butun oʻndan besh stakanni bashorat qiladi. Shuning uchun chiziqni faqat burchak koeffitsiyenti belgilaydi.**
   *The second formula says one important thing: the line always passes through the mean point. At twenty-one point eight degrees it predicts exactly thirty-nine point five cups. So the slope alone fixes the line.*
   ▸ the line pivoting about the red mean point
7. **Hisoblaymiz. Qirq toʻqqiz butun oʻndan oltini oʻttiz bir butun oʻndan toʻqqizga boʻlamiz: bir butun yuzdan ellik besh stakan har bir darajaga. Ozod had — besh butun oʻndan olti stakan.**
   *Let's compute. Forty-nine point six divided by thirty-one point nine: one point five five cups per degree. The intercept: five point six cups.*
   ▸ b = 49.6 / 31.9 = 1.55;  a = 39.49 − 1.55 × 21.81 = 5.6;  ŷ = 5.6 + 1.55x
8. **Demak, har bir qoʻshimcha daraja taxminan bir yarim stakan qoʻshadi. Ertaga uch daraja issiq boʻlsa, taxminan besh stakan koʻproq tayyorlaymiz. Qahvaxonaning savoliga javob — shu.**
   *So each extra degree adds about one and a half cups. If tomorrow is three degrees warmer, we prepare about five cups more. That is the shop's answer.*
   ▸ 3 × 1.55 = 4.7 ≈ 5
9. **Ozod hadni esa jiddiy qabul qilmaymiz: bu nol darajadagi savdo, biz esa bunday sovuq kunni hech koʻrmaganmiz.**
   *We do not take the intercept seriously: it is the sales at zero degrees, and we never saw a day that cold.*
10. **Burchak koeffitsiyentiga yana bir tomondan qaraylik. U ar karra savdo tarqoqligining harorat tarqoqligiga nisbatiga teng. Demak, bir standart chetlanish, yaʼni besh butun yuzdan oltmish besh daraja issiqroq kun sakkiz butun oʻndan sakkiz stakan koʻproq sotadi — bu savdoning bitta emas, atigi nol butun yuzdan yetmish yetti standart chetlanishi. Bogʻlanish mukammal boʻlmasa, bashorat oʻrtachaga yaqinroq qoladi.**
    *Let's look at the slope from another side. It equals r times the spread of sales over the spread of temperature. So a day one standard deviation warmer, five point six five degrees, sells eight point eight more cups: not one standard deviation of sales, only zero point seven seven of one. When the relationship is not perfect, the prediction stays closer to the mean.*
    ▸ b = r · s_y / s_x; a step of 1 s_x to the right, a rise of 0.77 s_y up
11. **Sunʼiy intellektda bu mashinali oʻqitishning eng kichik koʻrinishi: parametrlarni shunday tanlaymiz-ki, bashoratlar berilganlardan iloji boricha kam adashsin. Katta modellar ham aynan shu ishni qiladi, faqat parametrlari milliardlab.**
    *In AI this is the smallest act of machine learning: we choose the parameters so the predictions miss the data as little as possible. Large models do the very same thing, only with billions of parameters.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yigirma besh darajali kunda chiziq nechta stakanni bashorat qiladi?**
    *Let's try it ourselves. Pause the video. How many cups does the line predict on a twenty-five-degree day?*
13. **Besh butun oʻndan oltiga bir butun yuzdan ellik besh karra yigirma beshni qoʻshamiz: taxminan qirq toʻrt stakan.**
    *Five point six plus one point five five times twenty-five: about forty-four cups.*
14. **Chiziq har bir kunni qanchalik yaxshi bashorat qildi? Keyingi boʻlimda.**
    *How well did the line predict each day? The next section.*

### 4-boʻlim · Section 4 — Qoldiqlar · Residuals
1. **Qoldiq — chiziq qanchaga adashgani: haqiqiy savdodan bashoratni ayiramiz.**
   *A residual is how far the line missed: the real sales minus the prediction.*
   ▸ e = y − ŷ; red vertical segments for the twelve largest
2. **Masalan, yigirma besh darajali bir kunda oʻttiz ikkiga yaqin stakan sotildi, chiziq esa qirq toʻrt butun oʻndan toʻrtni bashorat qilgan edi. Qoldiq — minus oʻn ikki butun oʻndan besh: bu kun kutilganidan ancha sokin oʻtdi.**
   *For example, on one twenty-five-degree day about thirty-two cups were sold, while the line predicted forty-four point four. The residual is minus twelve point five: the day was much quieter than expected.*
   ▸ the day at 25 °C: 31.9 − 44.4 = −12.5
3. **Eng kichik kvadratlar usuli qoldiqlar oʻrtachasini aynan nolga tenglaydi. Musbat va manfiy xatolar bir-birini yopadi, shuning uchun ularning faqat kattaligi muhim: odatda yetti butun oʻndan ikki stakan.**
   *Least squares makes the residuals average exactly zero. Positive and negative misses cancel, so only their size matters: typically seven point two cups.*
4. **Qoldiqlarni haroratga qarab chizamiz. Bu chizma — haqiqiy sinov.**
   *We plot the residuals against temperature. This plot is the real test.*
   ▸ the lower panel: residuals against temperature, a flat band around zero
5. **Bizda hech qanday naqsh yoʻq: egri chiziq ham, kengayib boruvchi voronka ham. Demak, toʻgʻri chiziq toʻgʻri shakl edi. Qoldiqlarda yoy koʻrinsa edi, chiziq haqiqiy tuzilmani oʻtkazib yuborgan boʻlardi.**
   *Ours shows no pattern: no curve, no widening funnel. So a line was the right shape. Had the residuals traced an arc, the line would have missed real structure.*
   ▸ beside it, two small sketches (labelled as illustrations): an arc and a funnel
6. **Boshqacha aytganda, chiziq haroratdan olish mumkin boʻlgan hamma narsani oldi. Qoldiqlarning harorat bilan korrelyatsiyasi aynan nol. Qolgan narsa — haroratdan boshqa sabablar: bayram, yomgʻir, yaqin atrofdagi tadbir.**
   *Put another way, the line took everything the temperature could tell. The residuals' correlation with temperature is exactly zero. What is left comes from causes other than temperature: a holiday, rain, an event nearby.*
7. **Sunʼiy intellektda istalgan regressiya modelini shunday tekshiramiz: xatolarini kirish qiymatlariga qarab chizamiz. Xatolarda naqsh qolsa, model oʻrganishi mumkin boʻlgan narsani oʻrganmagan.**
   *In AI, we check any regression model this way: we plot its errors against its inputs. If a pattern is left in the errors, the model has not learned something it could have.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Faraz qilaylik, boshqa bir yigirma besh darajali kunda oʻttiz besh stakan sotildi. Qoldiq qancha?**
   *Let's try it ourselves. Pause the video. Suppose another twenty-five-degree day sold thirty-five cups. What is the residual?*
9. **Oʻttiz beshdan qirq toʻrt butun oʻndan toʻrtni ayiramiz: minus toʻqqiz butun oʻndan toʻrt. Bu kun ham kutilganidan sokin, lekin odatdagi xatodan unchalik uzoq emas.**
   *Thirty-five minus forty-four point four: minus nine point four. This day was quieter than expected too, but not far beyond the typical miss.*
10. **Chiziq savdodagi oʻzgarishning qancha qismini tushuntirdi? Keyingi boʻlimda.**
    *How much of the variation in sales did the line explain? The next section.*

### 5-boʻlim · Section 5 — Ar kvadrat · R²
1. **Haroratni bilmasak, eng yaxshi bashoratimiz — oʻrtacha savdo, yaʼni gorizontal chiziq. Uning farqlari kvadratlarining yigʻindisi — oʻttiz sakkiz ming uch yuz sakson besh.**
   *Without the temperature, our best guess is the mean sales: a flat line. The sum of its squared gaps is thirty-eight thousand three hundred eighty-five.*
   ▸ top panel: a flat line at ȳ with red gaps; SS_tot = 38,385
2. **Haroratni bilsak, chiziqdan foydalanamiz. Uning farqlari kvadratlarining yigʻindisi — oʻn besh ming uch yuz qirq sakkiz.**
   *Knowing the temperature, we use the line. The sum of its squared gaps is fifteen thousand three hundred forty-eight.*
   ▸ bottom panel: the fitted line with its shorter gaps; SS_res = 15,348
3. **Ar kvadrat — chiziq yoʻqotgan ulush: birdan ikkinchisining birinchisiga nisbatini ayiramiz. Nol butun yuzdan oltmish chiqadi. Haroratni bilish kunlik savdo haqidagi taxminning oltmish foizini yoʻqotadi.**
   *R squared is the share the line removed: one minus the second over the first. It comes out at zero point six zero. Knowing the temperature removes sixty percent of the guesswork about a day's sales.*
   ▸ R² = 1 − 15,348 / 38,385 = 0.60
4. **Buni dispersiya orqali ham koʻrish mumkin. Savdoning dispersiyasi bir yuz yigirma sakkiz butun oʻndan toʻrt, chiziq atrofidagi qoldiqlar dispersiyasi esa ellik bir butun oʻndan besh — taxminan nol butun oʻndan toʻrt ulushi qoldi. Qolgan oltmish foizni harorat tushuntirdi.**
   *We can see it through the variance too. The sales' variance is one hundred twenty-eight point four, and the residuals' variance around the line is fifty-one point five: about zero point four of it is left. Temperature explained the other sixty percent.*
   ▸ two bars: 128.4 and 51.5; the gap between them shaded "60 %"
5. **Bitta oʻzgaruvchi boʻlsa, ar kvadrat aynan korrelyatsiyaning kvadrati. Aniqroq aytsak, ar — nol butun oʻn mingdan yetti ming yetti yuz qirq yetti, uning kvadrati — nol butun yuzdan oltmish.**
   *With one predictor, R squared is exactly the correlation squared. More precisely, r is zero point seven seven four seven, and its square is zero point six zero.*
   ▸ 0.7747² = 0.60
6. **Sunʼiy intellektda regressiya modelining sifati koʻpincha aynan ar kvadrat bilan aytiladi. Lekin oʻninchi maʼruzada koʻramiz: uni model oʻqitilgan berilganlarda emas, yangi berilganlarda oʻlchash kerak.**
   *In AI, a regression model's quality is often quoted as exactly this R squared. But as Lecture 10 shows, it must be measured on new data, not on the data the model was trained on.*
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Korrelyatsiya nol butun oʻndan besh boʻlsa, chiziq oʻzgarishning qancha qismini tushuntiradi?**
   *Let's try it ourselves. Pause the video. If the correlation were zero point five, what share of the variation would the line explain?*
8. **Nol butun oʻndan beshning kvadrati — nol butun yuzdan yigirma besh, yaʼni atigi chorak qismi. «Yarim» deb eshitiladigan korrelyatsiya oʻzgarishning toʻrtdan birini tushuntiradi.**
   *Zero point five squared is zero point two five: only a quarter. A correlation that sounds like "half" explains one quarter of the variation.*
9. **Lekin nega aynan kvadratlar? Bunga hali asos keltirmadik. Keyingi boʻlimda.**
   *But why squares at all? We have not justified that yet. The next section.*

### 6-boʻlim · Section 6 — Eng kichik kvadratlar — bu maksimal haqiqatga oʻxshashlik · Least squares is maximum likelihood
1. **Beshinchi maʼruzani eslaylik. Har bir kungi savdo chiziq qoʻshuv normal shovqin, deb faraz qilgan edik. Minus logarifmik haqiqatga oʻxshashlik ikki haddan iborat edi.**
   *Let's recall Lecture 5. We assumed each day's sales are the line plus normal noise. Minus the log-likelihood had two terms.*
   ▸ yᵢ ~ N(a + bxᵢ, σ²);  −ℓ = (n/2) log(2πσ²) + (1/2σ²) Σ (yᵢ − a − bxᵢ)²
2. **Birinchi hadda ey ham, bi ham yoʻq. Ikkinchi had — kvadratik farqlar yigʻindisi, musbat songa koʻpaytirilgan.**
   *The first term contains neither a nor b. The second is the sum of squared gaps, times a positive number.*
   ▸ the first term greyed out "ey va bi yoʻq"
3. **Demak, haqiqatga oʻxshashlikni maksimallashtirish va kvadratik farqlarni minimallashtirish — bitta ish. Eng kichik kvadratlar hech qachon tasodifiy tanlov boʻlmagan.**
   *So maximising the likelihood and minimising the squared gaps are the same act. Least squares was never an arbitrary choice.*
4. **Kvadrat qayerdan keldi? Beshinchi maʼruzada koʻrganimizdek, normal taqsimot zichligida eksponenta ichida farqning kvadrati turadi. Logarifm eksponentani olib tashlaydi, kvadrat esa qoladi.**
   *Where did the square come from? As we saw in Lecture 5, inside the exponential of the normal density sits the squared deviation. The logarithm removes the exponential, and the square stays.*
5. **Qoldiqlar tarqoqligi shovqinning sigmasini baholaydi: taxminan yetti butun oʻndan ikki stakan. Endi chiziq faqat bitta son emas, balki har bir haroratdagi butun normal egri chiziq.**
   *The spread of the residuals estimates the noise's sigma: about seven point two cups. Now the line is not just one number but a whole normal curve at every temperature.*
   ▸ small bell curves standing on the line at several temperatures
6. **Toʻrtinchi maʼruzadagi qoidani qoʻllaymiz: kunlarning taxminan toʻqson besh foizi chiziqdan ikki sigma ichida boʻlishi kerak. Tekshirdik: uch yuz kundan toʻqson besh butun oʻndan yetti foizi shu tasma ichida.**
   *We apply Lecture 4's rule: about ninety-five percent of days should fall within two sigma of the line. We checked: ninety-five point seven percent of the three hundred days lie inside that band.*
   ▸ a band of ±14.4 cups around the line; 95.7 % of the dots inside
7. **Sunʼiy intellekt kursi buni nega oʻrgatadi? Bu kursdagi eng kichik oʻqitilgan model: ikki parametr, maksimal haqiqatga oʻxshashlik bilan topilgan. Keyingi hamma modellar ey qoʻshuv bi eks oʻrniga kattaroq model qoʻyadi, lekin retsept oʻsha: minus logarifmik haqiqatga oʻxshashlikni yozamiz va minimallashtiramiz. Bi ga jarima qoʻshsak — Rij va Lasso chiqadi, buni oltinchi maʼruzada koʻrgandik.**
   *Why does an AI course teach this? It is the smallest trained model in the course: two parameters, found by maximum likelihood. Every later model swaps a plus b x for something bigger, but the recipe stays: write minus the log-likelihood and minimise it. Add a penalty on b and we get Ridge and Lasso, as Lecture 6 showed.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yigirma besh darajali kunda chiziq qirq toʻrt butun oʻndan toʻrt stakanni bashorat qiladi, sigma esa yetti butun oʻndan ikki. Savdo taxminan toʻqson besh foiz ehtimol bilan qaysi oraliqda boʻladi?**
   *Let's try it ourselves. Pause the video. On a twenty-five-degree day the line predicts forty-four point four cups, and sigma is seven point two. In what range will sales fall with about ninety-five percent probability?*
9. **Ikki sigma — oʻn toʻrt butun oʻndan toʻrt. Qirq toʻrt butun oʻndan toʻrtdan ayirib va qoʻshib: taxminan oʻttiz butun oʻndan birdan ellik sakkiz butun oʻndan sakkizgacha. Bu qahvaxona uchun «besh stakan koʻproq» degan javobdan ham foydaliroq.**
   *Two sigma is fourteen point four. Subtracting from and adding to forty-four point four: about thirty point one to fifty-eight point eight. For the shop, that is even more useful than "five cups more".*
   ▸ 44.4 ± 14.4 → 30.1 … 58.8
10. **Korrelyatsiya nimani koʻra olmaydi? Keyingi boʻlimda.**
    *What can the correlation not see? The next section.*

### 7-boʻlim · Section 7 — Korrelyatsiya koʻrmaydigan narsa · What the correlation cannot see
1. **Oʻsha uch yuz kun, lekin endi jami ichimliklar soni. Sovuq kunlarda issiq ichimliklar, issiq kunlarda muzli ichimliklar sotiladi, oʻrtacha kunlarda esa ikkalasi ham kam.**
   *The same three hundred days, but now total drinks. Cold days sell hot drinks, hot days iced ones, and mild days fewest of either.*
   ▸ the U-shaped scatter of total drinks against temperature
2. **Korrelyatsiya — minus nol butun yuzdan olti, toʻgʻri chiziq esa deyarli hech narsani tushuntirmaydi: ar kvadrat nol. Shu ikki songa qarab «harorat jami savdoga taʼsir qilmaydi» deb aytgan boʻlardik.**
   *The correlation is minus zero point zero six, and a straight line explains next to nothing: R squared is zero. On those two numbers we would say "temperature does not affect total sales".*
   ▸ the flat fitted line; r = −0.06, R² = 0.00
3. **Lekin rasmga qaraylik: bogʻlanish kuchli va yaqqol. Egri chiziq oʻzgarishning ellik besh foizini tushuntiradi. U yigirma ikki daraja atrofida eng pastga, taxminan ellik beshta ichimlikka tushadi.**
   *But let's look at the picture: the relationship is strong and obvious. A curve explains fifty-five percent of the variation. It bottoms out around twenty-two degrees, at about fifty-five drinks.*
   ▸ the curve drawn in; R² = 0.55; its lowest point marked
4. **Nega ar buni koʻrmadi? Kunlarni ikkiga boʻlaylik. Salqin yarmida korrelyatsiya minus nol butun yuzdan oltmish sakkiz: issiqlashgan sari kamroq ichiladi. Issiq yarmida plyus nol butun yuzdan oltmish toʻqqiz: issiqlashgan sari koʻproq. Ikki kuchli bogʻlanish qarama-qarshi yoʻnalishda, birga qoʻshilganda bir-birini yoʻqqa chiqaradi.**
   *Why did r miss it? Let's split the days in two. On the cool half the correlation is minus zero point six eight: the warmer, the fewer drinks. On the warm half it is plus zero point six nine: the warmer, the more. Two strong relationships in opposite directions cancel each other out when pooled.*
   ▸ the cloud split at 21.8 °C, each half with its own line: −0.68 left, +0.69 right
5. **Ar faqat bitta narsani oʻlchaydi — toʻgʻri chiziqli bogʻlanishni. Tushib, keyin koʻtariladigan bogʻlanishni u nol deb koʻrsatadi.**
   *r measures one thing only: straight-line association. A relationship that falls and then rises, it reports as nothing.*
6. **Birinchi maʼruzadagi Enskomb kvartetini eslaylik. Toʻrtta toʻplamda ham korrelyatsiya taxminan nol butun mingdan sakkiz yuz oʻn olti va chiziq bir xil edi. Endi bu soʻzlarning hammasi bizga tanish.**
   *Let's recall Anscombe's quartet from Lecture 1. All four sets shared a correlation of about zero point eight one six and the same line. Now every one of those words has a definition.*
   ▸ the four Anscombe panels, each with the same line
7. **Ar bir xil boʻlgani uchun ar kvadrat ham bir xil: nol butun yuzdan oltmish yetti. Har bir chiziq oʻzgarishning uchdan ikki qismini tushuntirgandek koʻrinadi. Lekin buni faqat birinchisi chindan ham qiladi.**
   *Sharing r, they also share R squared: zero point six seven. Each line seems to explain two thirds of the variation. Only the first truly does.*
8. **Qoldiqlar grafigi nimani koʻrsatardi? Ikkinchi toʻplamda qoldiqlar toza yoy chizadi: chetlarida manfiy, oʻrtada musbat — xuddi jami ichimliklardagi kabi notoʻgʻri shakl. Uchinchisida bitta qoldiq boshqalardan ajralib turadi: uch butun yuzdan yigirma toʻrt.**
   *What would the residual plot show? In the second set the residuals trace a clean arc: negative at the ends, positive in the middle, the wrong shape, just like total drinks. In the third, one residual stands apart from the rest: three point two four.*
   ▸ residual plots for II (an arc) and III (one tall bar)
9. **Toʻrtinchisida esa qoldiqlar grafigi ham jim. Uzoqdagi nuqtaning qoldigʻi aynan nol, chunki chiziq uning ustidan oʻtadi — butun chiziqni shu bitta nuqta belgilaydi. Buni faqat nuqtalarning oʻzini chizsak koʻramiz.**
   *In the fourth, even the residual plot stays silent. The far point's residual is exactly zero, because the line passes right through it: that single point decides the whole line. Only plotting the points themselves shows it.*
   ▸ set IV: the far point at (19, 12.5) on the line, its residual 0
10. **Demak, ishchi qoida: burchak koeffitsiyenti, ar va ar kvadrat — xulosa emas, qisqacha mazmun. Ularga ishonishdan oldin chiziqni ham, qoldiqlarni ham, nuqtalarning oʻzini ham chizib koʻramiz.**
    *So the working rule: the slope, r and R squared are a summary, never a verdict. Before believing them, we plot the line, the residuals and the points themselves.*
11. **Sunʼiy intellektda belgilarni faqat korrelyatsiyaga qarab tanlasak, jami ichimliklar uchun haroratni foydasiz deb tashlab yuborardik. Neyron tarmoqlar va qaror daraxtlari esa bunday egri bogʻlanishni oʻzi topa oladi.**
    *In AI, if we chose features by correlation alone, we would throw temperature away as useless for total drinks. Neural networks and decision trees, though, can find a curved relationship like this on their own.*
12. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Enskomb toʻplamlarida korrelyatsiya taxminan nol butun mingdan sakkiz yuz oʻn olti. Ar kvadrat qancha va u nimani aytadi?**
    *Let's think it over. Pause the video. In Anscombe's sets the correlation is about zero point eight one six. What is R squared, and what does it say?*
13. **Nol butun mingdan sakkiz yuz oʻn oltining kvadrati — taxminan nol butun yuzdan oltmish yetti. Chiziq oʻzgarishning uchdan ikki qismini tushuntirgandek koʻrinadi. Lekin bu faqat birinchi toʻplam uchun rost, va buni son emas, rasm aytadi.**
    *Zero point eight one six squared is about zero point six seven. The line appears to explain two thirds of the variation. That is true only for the first set, and the picture tells us so, not the number.*
14. **Korrelyatsiya kuchli boʻlsa, biri ikkinchisiga sabab boʻladimi? Keyingi boʻlimda.**
    *If a correlation is strong, does one cause the other? The next section.*

### 8-boʻlim · Section 8 — Korrelyatsiya sababiylik emas · Correlation is not causation
1. **Qahvaxonaning muzli qahva savdosi qoʻshni doʻkonda sotilgan quyosh koʻzoynaklari bilan kuchli bogʻlangan. Lekin biri ikkinchisiga sabab emas: ikkalasiga ham issiq havo sabab.**
   *The shop's iced coffee sales are strongly correlated with the sunglasses sold next door. Neither causes the other: hot weather causes both.*
   ▸ a sun with two arrows, to "muzli qahva" and to "quyosh koʻzoynagi"; a dashed line between them labelled r
2. **Ikki miqdorni birga boshqaradigan uchinchi miqdor chalkashtiruvchi omil deb ataladi.**
   *A third quantity that drives two others is called a confounder.*
3. **Ar ham, burchak koeffitsiyenti ham, ar kvadrat ham buni sezmaydi. Ular ikki ustun sonlardan hisoblanadi va bu sonlarni nima yuzaga keltirganini bilmaydi.**
   *Neither r, nor the slope, nor R squared can detect this. They are computed from two columns of numbers and know nothing about what produced them.*
4. **Ikkinchi maʼruzada buning keskinroq koʻrinishini koʻrgandik — Simpson paradoksi. Berklida umumiy berilganlar bir tomonni koʻrsatdi, fakultetlarni hisobga olganimizda esa taqqoslash teskari aylandi. U yerda chalkashtiruvchi omil — fakultet edi.**
   *Lecture 2 showed us the sharper version: Simpson's paradox. At Berkeley the pooled data pointed one way, and once we took the departments into account the comparison reversed. There the confounder was the department.*
   ▸ Lecture 2's Berkeley bars, flipping when split by department
5. **Amaliy ajratish shunday. Bashorat uchun korrelyatsiya yetarli: qoʻshni doʻkondagi koʻzoynaklar savdosi ertangi muzli qahva savdosini haqiqatan bashorat qilishga yordam beradi.**
   *The practical split is this. For prediction, correlation is enough: the sunglasses sold next door genuinely help forecast tomorrow's iced coffee.*
6. **Aralashuv uchun esa u befoyda: koʻzoynaklarni tekinga tarqatsak ham, bitta ortiqcha stakan sotilmaydi.**
   *For intervention it is useless: handing out free sunglasses will not sell one extra cup.*
   ▸ two columns: "bashorat ✓" and "aralashuv ✗"
7. **Sunʼiy intellektda tavsiya tizimi tarixiy berilganlardagi korrelyatsiyadan bashorat qila oladi. Lekin «bu tugmani oʻzgartirsak, sotuv oshadimi?» degan savolga faqat tajriba javob beradi: foydalanuvchilarni tasodifiy ikki guruhga ajratib, solishtiramiz. Bu A/B sinov.**
   *In AI, a recommender can predict from the correlations in historical data. But the question "if we change this button, will sales rise?" only an experiment answers: we split users at random into two groups and compare. That is an A/B test.*
8. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Muzli qahva va issiq ichimliklar savdosi orasida kuchli manfiy korrelyatsiya bor. Issiq ichimlik narxini oshirsak, muzli qahva koʻproq sotiladimi?**
   *Let's think it over. Pause the video. Iced coffee and hot drink sales have a strong negative correlation. If we raise the price of hot drinks, will more iced coffee be sold?*
9. **Bu korrelyatsiyadan buni bilib boʻlmaydi. Ikkalasini ham harorat boshqaradi: issiq kunda biri oshadi, ikkinchisi kamayadi. Bu birinchi qismda aniq koʻrinadi.**
   *This correlation cannot tell us. Both are driven by the temperature: on a hot day one rises and the other falls. Part one shows this clearly.*
10. **Mana shu bilan nolinchi qismni tugatamiz. Lekin yozuvlarda odatda ikkitadan koʻp ustun boʻladi. Ularning hammasini birdaniga qanday tasvirlaymiz? Birinchi qismda.**
    *That completes part zero. But records usually have more than two columns. How do we describe them all at once? In part one.*

## Part 1 — Koʻp oʻlchovli statistika
▸ part card "1-qism · Koʻp oʻlchovli statistika"

### 9-boʻlim · Section 9 — Kovariatsiya va korrelyatsiya matritsasi · The covariance and correlation matrices
1. **Nolinchi qismda bitta juftlik bilan ishladik. Haqiqiy yozuvlarda ustunlar koʻproq: qahvaxona har kuni haroratni, muzli qahvalarni va issiq ichimliklarni yozib boradi.**
   *Part zero handled one pair. Real records have more columns: the shop logs the temperature, the iced coffees and the hot drinks every day.*
   ▸ a table with three columns: harorat, muzli qahva, issiq ichimlik
2. **Key ta miqdorda juftliklar soni — key karra key minus birni ikkiga boʻlganimiz. Uchta ustunda uchta juftlik, oʻnta ustunda qirq beshta, yuzta ustunda esa toʻrt ming toʻqqiz yuz ellikta. Ularni birma-bir aytib chiqish tezda imkonsiz boʻladi.**
   *With k quantities there are k times k minus one over two pairs. Three columns give three pairs, ten give forty-five, and a hundred give four thousand nine hundred fifty. Quoting them one at a time soon becomes impossible.*
   ▸ k(k − 1)/2: 3 → 3, 10 → 45, 100 → 4,950
3. **Shuning uchun ularni kvadrat jadvalga yigʻamiz. Toʻrtinchi maʼruzada ikki ustun uchun kovariatsiya matritsasini qurgan edik, endi faqat oʻlchami oʻzgaradi.**
   *So we collect them in a square table. Lecture 4 built the covariance matrix for two columns; only its size changes now.*
4. **Diagonalda har bir miqdorning dispersiyasi, diagonaldan tashqarida — har bir juftlikning kovariatsiyasi. Matritsa simmetrik, chunki eks bilan uay ning kovariatsiyasi uay bilan eks nikiga teng.**
   *On the diagonal sits each quantity's variance; off the diagonal, each pair's covariance. The matrix is symmetric, because the covariance of x with y equals that of y with x.*
   ▸ the 3 × 3 matrix: 31.9, 49.6, −69.5 / 49.6, 128.4, −107.4 / −69.5, −107.4, 206.0
5. **Minus bir yuz yetti butun oʻndan toʻrt qirq toʻqqiz butun oʻndan oltidan kuchliroq bogʻlanishmi? Kovariatsiya matritsasi buni ayta olmaydi: uning kataklarida uch xil birlik juftligi bor. Birinchi boʻlimdagi muammoning oʻzi.**
   *Is minus one hundred seven point four a stronger link than forty-nine point six? The covariance matrix cannot say: its cells carry three different pairs of units. The very problem of section one.*
6. **Yechim ham oʻsha: har bir katakni ikkala standart chetlanishga boʻlamiz. Bu korrelyatsiya matritsasi. Uning diagonalida faqat birlar turadi, chunki har bir miqdor oʻzi bilan mukammal bogʻlangan.**
   *The fix is the same: we divide every cell by both standard deviations. That is the correlation matrix. Its diagonal holds only ones, because every quantity is perfectly correlated with itself.*
   ▸ the correlation matrix as a coloured grid: 1, 0.77, −0.86 / 0.77, 1, −0.66 / −0.86, −0.66, 1
7. **Endi solishtirsa boʻladi. Harorat va issiq ichimliklar — minus nol butun yuzdan sakson olti: jadvaldagi eng kuchli bogʻlanish, harorat va muzli qahvadagi nol butun yuzdan yetmish yettidan ham kuchliroq.**
   *Now the cells are comparable. Temperature and hot drinks, minus zero point eight six, is the strongest relationship in the table, stronger than temperature and iced coffee at zero point seven seven.*
8. **Muzli va issiq ichimliklar orasida minus nol butun yuzdan oltmish olti. Lekin biri ikkinchisiga sabab emas: ikkalasini ham harorat boshqaradi, qarama-qarshi yoʻnalishda. Nolinchi qismning oxiridagi chalkashtiruvchi omil endi jadvalda koʻrinib turibdi.**
   *Iced and hot drinks correlate at minus zero point six six. Yet neither causes the other: the temperature drives both, in opposite directions. The confounder from the end of part zero is now visible in the table.*
9. **Buni tekshirish ham mumkin. Har ikki ichimlikdan haroratning taʼsirini olib tashlaymiz, yaʼni toʻrtinchi boʻlimdagidek ularning qoldiqlarini olamiz. Qoldiqlar orasidagi korrelyatsiya — bor-yoʻgʻi nol butun yuzdan bir. Minus nol butun yuzdan oltmish oltining deyarli hammasi harorat edi.**
   *We can check it too. We take the temperature's effect out of both drinks, that is, we take their residuals as in section four. The correlation between the residuals is just zero point zero one. Almost all of the minus zero point six six was the temperature.*
   ▸ two residual columns side by side, their scatter a round cloud; r = −0.66 → 0.01
10. **Matritsa simmetrik va diagonali birlardan iborat, shuning uchun faqat diagonaldan yuqoridagi uchta katak maʼlumot beradi.**
    *The matrix is symmetric with ones on the diagonal, so only the three cells above the diagonal carry information.*
11. **Sunʼiy intellektda berilganlar bilan ishlash koʻpincha aynan shu rasmdan boshlanadi: belgilarning korrelyatsiya matritsasini chizamiz. Bir-biri bilan juda kuchli bogʻlangan ikki belgi deyarli bir xil maʼlumot beradi, birini olib tashlasa boʻladi.**
    *In AI, working with data often begins with exactly this picture: we draw the features' correlation matrix. Two features very strongly correlated with each other carry nearly the same information, and one can be dropped.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beshta ustunda nechta juftlik bor? Mingta ustunda-chi?**
    *Let's try it ourselves. Pause the video. How many pairs do five columns have? And a thousand?*
13. **Besh karra toʻrtni ikkiga boʻlamiz: oʻnta. Ming karra toʻqqiz yuz toʻqson toʻqqizni ikkiga boʻlamiz: toʻrt yuz toʻqson toʻqqiz ming besh yuzta. Bunday jadvalni koʻz bilan oʻqib boʻlmaydi, unga boshqa usul kerak.**
    *Five times four over two: ten. A thousand times nine hundred ninety-nine over two: four hundred ninety-nine thousand five hundred. No one reads a table like that by eye; it needs another method.*
14. **Bu usul matritsaning ichidan qanday yoʻnalishlarni topadi? Keyingi boʻlimda.**
    *What directions does that method find inside the matrix? The next section.*

### 10-boʻlim · Section 10 — Xos vektorlar · Eigenvectors of the covariance matrix
1. **Nolinchi qismdagi nuqtalar bulutiga yana qaraylik. U qiyshaygan ellips, va uning tabiiy oʻqlari bulut boʻylab va bulutga koʻndalang ketadi. Ularning hech biri harorat oʻqi ham, stakanlar oʻqi ham emas.**
   *Look again at the cloud from part zero. It is a tilted ellipse, and its natural axes run along the cloud and across it. Neither is the temperature axis or the cups axis.*
   ▸ the scatter with Lecture 4's ellipse; its long and short axes drawn dashed
2. **Har bir kunni ikki son bilan — harorat va stakanlar bilan — tasvirlash ortiqcha: birini bilsak, ikkinchisining koʻp qismini bilamiz. Ar teng nol butun yuzdan yetmish yetti aynan shuni aytgan edi.**
   *Describing each day by two numbers, temperature and cups, is largely redundant: knowing one tells us most of the other. That is what r equal to zero point seven seven said.*
3. **Shuning uchun aniqroq savol beramiz: oʻzgarishning koʻp qismini bitta yoʻnalish qamrab oladimi? Agar shunday boʻlsa, har bir kun uchun bitta son ikki sondek yaxshi boʻlishi mumkin.**
   *So we ask a sharper question: is there one direction that captures most of the variation? If there is, one number per day might be almost as good as two.*
4. **Javob kovariatsiya matritsasining ichida: toʻrtinchi maʼruzada ellipsni aynan u chizgan edi. Uni chiqarib olish — xos qiymatlar masalasi.**
   *The answer sits inside the covariance matrix: in Lecture 4 it is what drew the ellipse. Getting it out is an eigenvalue problem.*
5. **Xos vektor — matritsa faqat choʻzadigan, lekin burmaydigan yoʻnalish. Sigma karra vi teng lambda karra vi. Xos qiymat lambda — choʻzilish koeffitsiyenti. Kovariatsiya matritsasi uchun esa lambda — berilganlarning shu yoʻnalish boʻylab dispersiyasi.**
   *An eigenvector is a direction the matrix only stretches, never turns: sigma times v equals lambda times v. The eigenvalue lambda is the stretch factor. For a covariance matrix, lambda is the variance of the data along that direction.*
   ▸ Σv = λv; an arbitrary arrow that Σ turns, then the eigenvector that Σ only lengthens
6. **Harorat va muzli qahva matritsasi uchun: birinchi xos qiymat — bir yuz qirq toʻqqiz butun oʻndan uch, uning yoʻnalishi — nol butun yuzdan oʻttiz toʻqqiz va nol butun yuzdan toʻqson ikki. Ikkinchisi — oʻn bir, yoʻnalishi unga perpendikulyar.**
   *For the temperature-and-iced-coffee matrix: the first eigenvalue is one hundred forty-nine point three, along the direction zero point three nine, zero point nine two. The second is eleven, along a direction perpendicular to it.*
   ▸ λ₁ = 149.3, v₁ = (0.39, 0.92);  λ₂ = 11.0, v₂ = (−0.92, 0.39)
7. **Ikki yoʻnalishning skalyar koʻpaytmasi nol, yaʼni ular perpendikulyar. Simmetrik matritsada bu doim shunday.**
   *The two directions' dot product is zero: they are perpendicular. A symmetric matrix always obliges.*
8. **Va dispersiya saqlanadi: bir yuz qirq toʻqqiz butun oʻndan uchga oʻn birni qoʻshsak, bir yuz oltmish butun oʻndan uch chiqadi — aynan oʻttiz bir butun oʻndan toʻqqiz qoʻshuv bir yuz yigirma sakkiz butun oʻndan toʻrt. Parchalash oʻzgarishni yaratmaydi ham, yoʻqotmaydi ham, faqat uni yaxshiroq oʻqlarga qayta taqsimlaydi.**
   *And the variance is conserved: one hundred forty-nine point three plus eleven is one hundred sixty point three, exactly thirty-one point nine plus one hundred twenty-eight point four. The decomposition neither creates nor destroys variation; it only redistributes it onto better axes.*
   ▸ 149.3 + 11.0 = 160.3 = 31.9 + 128.4
9. **Birinchi yoʻnalish bulutning uzun oʻqi boʻylab, harorat oʻqidan oltmish yetti daraja burchak ostida ketadi: «issiq va gavjum — salqin va sokin» yoʻnalishi. Ikkinchisi — kun oʻz haroratiga nisbatan qanchalik gʻayrioddiy ekani, yaʼni nolinchi qismdagi qoldiqning boshqa koʻrinishi.**
   *The first direction runs up the long axis of the cloud, sixty-seven degrees from the temperature axis: the "warm and busy versus cool and quiet" direction. The second is how unusual a day is for its temperature: the residual of part zero in another guise.*
   ▸ the two arrows from the mean point, v₁ long, v₂ short
10. **Lambdani yana bir tomondan tushunaylik. Har bir kunni birinchi yoʻnalishga proyeksiyalab, bitta son olamiz. Shu uch yuz sonning dispersiyasi — aynan bir yuz qirq toʻqqiz butun oʻndan uch, ikkinchi yoʻnalishda esa oʻn bir. Xos qiymat — oʻsha yoʻnalishdagi tarqoqlikning oʻzi.**
    *Let's understand lambda from one more side. Project each day onto the first direction, and we get one number. The variance of those three hundred numbers is exactly one hundred forty-nine point three; along the second direction, eleven. An eigenvalue is the spread along its direction.*
    ▸ the dots sliding onto the v₁ axis, forming a long strip; var = 149.3
11. **Ulushlarda: butun oʻzgarishning toʻqson uch butun oʻndan ikki foizi birinchi yoʻnalish boʻylab, atigi olti butun oʻndan sakkiz foizi unga koʻndalang.**
    *As shares: ninety-three point two percent of all the variation lies along the first direction, and only six point eight percent across it.*
    ▸ 93.2 % | 6.8 %
12. **Sunʼiy intellektda Gauss aralashmasi modelidagi har bir ellips ham shu xos vektorlar bilan chiziladi, graflar ustidagi spektral usullar ham xos vektorlarga tayanadi.**
    *In AI, every ellipse of a Gaussian mixture model is drawn by these eigenvectors, and spectral methods on graphs rest on eigenvectors too.*
13. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Lambda — dispersiya. Har bir yoʻnalish boʻylab standart chetlanish qancha?**
    *Let's try it ourselves. Pause the video. Lambda is a variance. What is the standard deviation along each direction?*
14. **Bir yuz qirq toʻqqiz butun oʻndan uchning ildizi — oʻn ikki butun oʻndan ikki, oʻn birning ildizi — uch butun oʻndan uch. Bulut koʻndalangiga qaraganda boʻyiga taxminan toʻrt baravar keng.**
    *The square root of one hundred forty-nine point three is twelve point two, and of eleven, three point three. The cloud is about four times wider along its length than across it.*
    ▸ √149.3 = 12.2, √11.0 = 3.3
15. **Ikki sonni bittaga almashtirsak nima boʻladi? Keyingi boʻlimda.**
    *What happens if we replace two numbers with one? The next section.*

### 11-boʻlim · Section 11 — Bosh komponentalar tahlili · That was PCA
1. **Har bir kunning ikki sonini bitta son bilan — uning birinchi yoʻnalish boʻylab qayerda turgani bilan — almashtiramiz. Oʻzgarishning toʻqson uch butun oʻndan ikki foizini saqlaymiz, olti butun oʻndan sakkiz foizini tashlaymiz. Ikki ustun bitta boʻldi, va narxi oʻlchangan.**
   *We replace each day's two numbers with one: where it sits along the first direction. We keep ninety-three point two percent of the variation and drop six point eight. Two columns became one, at a measured price.*
   ▸ the dots collapse onto the v₁ line; 93.2 % kept
2. **Bu bosh komponentalar tahlilining oʻzi. Kovariatsiya matritsasini xos vektorlarga ajratamiz, xos qiymatlarni kattadan kichikka saralaymiz, eng kattalarini qoldiramiz va berilganlarni ularga proyeksiyalaymiz.**
   *That is principal component analysis, in full. We decompose the covariance matrix into eigenvectors, sort the eigenvalues from largest to smallest, keep the top few directions, and project the data onto them.*
   ▸ four steps in a row: Σ → λ, v → saralash → proyeksiya
3. **Xos qiymatlar ulushi — tushuntirilgan dispersiya ulushi. Odatda toʻqson yoki toʻqson besh foizga yetguncha komponentalar qoldiramiz va nechta kerak boʻlganini sanaymiz.**
   *The eigenvalue shares are the explained variance. We usually keep components until they reach ninety or ninety-five percent, and count how many it took.*
4. **Uchala ustunimizda ham buni koʻrish mumkin. Standartlashtirilgan uch ustunda birinchi yoʻnalish oʻzgarishning sakson toʻrt butun oʻndan toʻrt foizini, birinchi ikkitasi esa toʻqson olti foizini oladi. Uchta son oʻrniga ikkitasi yetarli.**
   *We can see it on all three columns too. For the three standardized columns, the first direction holds eighty-four point four percent of the variation, and the first two hold ninety-six percent. Two numbers instead of three are enough.*
   ▸ a bar for each component: 84.4 %, 11.6 %, 4.0 %; the running total 84.4 → 96.0 → 100
5. **Lekin bitta ogohlantirish. Birinchi yoʻnalish nol butun yuzdan oʻttiz toʻqqiz va nol butun yuzdan toʻqson ikki — u stakanlar tomonga qattiq ogʻgan. Sababi stakanlar muhimroq ekanida emas, ular kattaroq sonlarda tebranishida: dispersiyasi bir yuz yigirma sakkiz butun oʻndan toʻrt, haroratniki esa oʻttiz bir butun oʻndan toʻqqiz.**
   *But one warning. The first direction, zero point three nine, zero point nine two, leans hard toward cups. Not because cups matter more, but because they vary over bigger numbers: a variance of one hundred twenty-eight point four against the temperature's thirty-one point nine.*
6. **Haroratni Farengeytda yozsak, uning dispersiyasi uch butun yuzdan yigirma toʻrt baravar oshadi. Oʻqlar buriladi va toʻqson uch butun oʻndan ikki foiz sakson sakkiz butun oʻndan toʻqqiz foizga aylanadi. Kovariatsiya matritsasi biz bergan birliklarda javob beradi.**
   *Record the temperatures in Fahrenheit and their variance is multiplied by three point two four. The axes swing, and ninety-three point two percent becomes eighty-eight point nine. A covariance matrix answers in whatever units we handed it.*
   ▸ °C → °F: the arrows swing; 93.2 % → 88.9 %
7. **Yechim — avval standartlashtirish. Toʻrtinchi maʼruzadagidek har bir ustunni zed-qiymatlarga almashtiramiz. Har bir dispersiya birga teng boʻladi, standartlashtirilgan berilganlarning kovariatsiya matritsasi esa aynan korrelyatsiya matritsasining oʻzi.**
   *The fix is to standardize first. As in Lecture 4, we replace each column by its z-scores. Every variance becomes one, and the covariance matrix of standardized data is exactly the correlation matrix.*
8. **Sunʼiy intellektda bu ikki narsani anglatadi. Mingta bir-biriga bogʻlangan ustunli berilganlarda kamdan-kam hollarda mingta yoʻnalishlik maʼlumot boʻladi: bosh komponentalar tahlili haqiqatda nechta borligini oʻlchaydi, bu oʻlchamni kamaytirish deb ataladi. Va bu tahlildan oldin deyarli doim standartlashtirish qadami turadi.**
   *In AI this means two things. Data with a thousand correlated columns rarely has a thousand directions' worth of information: PCA measures how many it really has, and that is called dimensionality reduction. And that analysis is almost always preceded by a standardizing step.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Korrelyatsiya matritsasining xos qiymatlari bir qoʻshuv ar va bir minus ar. Ar nol butun yuzdan yetmish yetti boʻlsa, ular qancha va ulushlari qanday?**
   *Let's try it ourselves. Pause the video. The correlation matrix's eigenvalues are one plus r and one minus r. With r equal to zero point seven seven, what are they, and what are their shares?*
10. **Bir butun yuzdan yetmish yetti va nol butun yuzdan yigirma uch, yigʻindisi ikki. Ulushlar — sakson sakkiz butun oʻndan yetti va oʻn bir butun oʻndan uch foiz. Toʻqson uch butun oʻndan ikki emas: oʻsha berilganlar, halol javob. Ustunlar bir xil birlikda boʻlmasa, avval standartlashtiramiz.**
    *One point seven seven and zero point two three, adding up to two. The shares are eighty-eight point seven and eleven point three percent. Not ninety-three point two: the same data, an honest answer. Unless the columns share units, we standardize first.*
    ▸ 1 + 0.77 = 1.77, 1 − 0.77 = 0.23; 88.7 % | 11.3 %
11. **Bu gʻoyalar keyin qayerda kerak boʻladi? Oʻninchi maʼruzada: bu yerdagi nol butun yuzdan oltmishlik ar kvadrat chiziq oʻqitilgan kunlarning oʻzida oʻlchandi, bu esa uni maqtab yuboradi. Halol son uchun yangi berilganlar va kross-validatsiya kerak.**
    *Where do these ideas go next? In Lecture 10: the R squared of zero point six zero here was measured on the very days the line was fitted to, which flatters it. An honest number needs new data and cross-validation.*
12. **Birinchi modulda bosh komponentalar tahlilini geometrik tarzda, eng kam yoʻqotadigan proyeksiya sifatida keltirib chiqaramiz va aynan shu yerga kelamiz. Rij va Lasso — eng kichik kvadratlar qoʻshuv koeffitsiyentlarga jarima. Logistik regressiya esa oʻsha retsept, faqat normal shovqin oʻrniga Bernulli natija, shuning uchun kvadratik xato oʻrnida kross-entropiya turadi.**
    *In Module 1 we derive PCA geometrically, as the projection that loses the least, and arrive right here. Ridge and Lasso are least squares plus a penalty on the coefficients. And logistic regression is the same recipe with a Bernoulli outcome instead of normal noise, so cross-entropy takes the place of squared error.*
13. **Keling, maʼruzani yakunlaylik. Kovariatsiya juftlik qaysi tomonga birga oʻzgarishini aytadi, korrelyatsiya esa qanchalik kuchli ekanini — birliksiz, minus birdan birgacha. Eng kichik kvadratlar usuli chiziqni oʻrtacha nuqta orqali oʻtkazadi va normal shovqinda u maksimal haqiqatga oʻxshashlikning oʻzi.**
    *Let's wrap up the lecture. The covariance says which way a pair moves together, and the correlation how strongly: unit-free, between minus one and one. Least squares puts the line through the mean point, and with normal noise it is maximum likelihood itself.*
14. **Ar kvadrat — chiziq tushuntirgan ulush, bitta oʻzgaruvchida u ar ning kvadrati. Notoʻgʻri shaklni esa son emas, qoldiqlar grafigi koʻrsatadi. Ar faqat toʻgʻri chiziqni koʻradi, va hech qanday korrelyatsiya sababiylikni isbotlamaydi.**
    *R squared is the share the line explains, and with one predictor it is r squared. A wrong shape is revealed by the residual plot, not by the number. r sees straight lines only, and no correlation proves causation.*
15. **Kovariatsiya matritsasi hamma juftliklarni birdaniga saqlaydi. Uning xos vektorlari — berilganlar haqiqatda oʻzgaradigan yoʻnalishlar, xos qiymatlari — shu yoʻnalishlardagi dispersiya. Eng kattalarini qoldirish — bosh komponentalar tahlili, ustunlar bir xil birlikda boʻlmasa, standartlashtirilgandan keyin.**
    *The covariance matrix holds every pair at once. Its eigenvectors are the directions the data really varies along, and its eigenvalues the variance along them. Keeping the largest few is PCA, after standardizing unless the columns share units.*
16. **Mana shu bilan toʻqqizinchi maʼruzamizni tugatamiz. Keyingi maʼruzada modellarni baholash va gipotezalarni tekshirish bilan tanishamiz.**
    *That brings our ninth lecture to an end. In the next lecture, we meet model evaluation and hypothesis testing.*
