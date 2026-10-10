# Lecture 1 — video narration (draft for approval)

Lecture 1 split into **14 short videos**: Part 0 (Data & descriptive statistics) = videos 1–9, Part 1 (Probability) = videos 10–14.
Each video: problem first → concept as the answer → one AI use → a hands-on pause → the problem the next video solves.

**Voice:** "we", not "you" — *keling, …-aylik*, *tasavvur qilamiz*, *hisoblaymiz*, *misolimizda*; each video opens with
*Assalomu alaykum, aziz doʻstlar*, transitions use *Xoʻp, endi* / *Mana* / *Demak*. The only line addressed to the viewer
is *Videoni toʻxtating* on the pause card.

**Numbers:** every figure below comes from `video/statistics/raw/l01_numbers.json` / `l01_figures.txt`
(produced by `capture_l01.py`, asserted against the slides). Narration spells them; the screen shows digits.

Format per line: **UZ** (what your voice says) · *EN* (English track) · ▸ visual.

---

## Part 0 — Maʼlumot va tavsifiy statistika

### Video 1 — Maʼlumot turlari · Data types
1. **Assalomu alaykum, aziz doʻstlar. Statistikada birinchi savol hisob-kitob emas. Birinchi savol: qoʻlimizdagi maʼlumot qanday turdagi maʼlumot?**
   *Hello, dear friends. In statistics, the first question is not a calculation. The first question is: what kind of data do we have?*
   ▸ six cards drop in: koʻz rangi · tugʻilgan shahar · baho · farzandlar soni · maosh · boʻy
2. **Tasavvur qilamiz, ikki kishining tugʻilgan shahrini qoʻshib, ikkiga boʻlmoqchimiz. Toshkent qoʻshuv Samarqand, boʻlinsin ikki. Bu hech qanday maʼnoga ega emas.**
   *Let's imagine we add up two people's cities of birth and divide by two. Tashkent plus Samarkand, divided by two. That means nothing.*
   ▸ "(Toshkent + Samarqand) ÷ 2 = ?" then a red cross
3. **Demak, ayrim maʼlumotlar son emas, balki toifa. Bularni kategorial maʼlumot deymiz.**
   *So some data are not numbers at all, but categories. We call them categorical data.*
   ▸ screen splits: left bin "kategorial", right bin "sonli"
4. **Koʻz rangi yoki tugʻilgan shaharda hech qanday tartib yoʻq. Bu nominal maʼlumot.**
   *Eye colour and city of birth have no natural order. That is nominal data.*
   ▸ two cards slide into "nominal", shuffled freely
5. **Baho esa past, oʻrta, yuqori — bu yerda tartib bor, lekin oraliqlari teng emas. Bu tartibli, yaʼni ordinal maʼlumot.**
   *A rating of low, medium, high does have an order, but the steps are not equal. That is ordinal data.*
   ▸ past → oʻrta → yuqori on a line with unequal gaps
6. **Xoʻp, endi sonli maʼlumotga oʻtaylik. Farzandlar sonini sanaymiz: bir, ikki, uch. Ikki yarim farzand boʻlmaydi. Bu diskret maʼlumot.**
   *Now let's move to numerical data. We count children: one, two, three. There is no such thing as two and a half children. That is discrete data.*
   ▸ number line, dots only on whole numbers; 2.5 crossed out
7. **Maosh yoki boʻy esa shkalada oʻlchanadi va oraliqdagi istalgan qiymatni olishi mumkin. Bu uzluksiz maʼlumot.**
   *Salary and height are measured on a scale, and can take any value in between. That is continuous data.*
   ▸ a marker glides along a ruler: 172 → 172.4 → 172.43
8. **Nima uchun bu muhim? Chunki maʼlumot turi qaysi hisob-kitob toʻgʻri ekanini belgilaydi. Oʻrtacha qiymat va standart chetlanish faqat sonli maʼlumot uchun maʼnoli. Kategorial maʼlumotni esa sanaymiz va ulushini hisoblaymiz.**
   *Why does this matter? Because the type of data decides which calculations make sense. A mean or a standard deviation only means something for numerical data. Categorical data we count, and turn into proportions.*
   ▸ the 2×2 map, with "sanash, ulush" under categorical and "oʻrtacha, chetlanish" under numerical
9. **Sunʼiy intellektda ham xuddi shunday: modelga shahar nomini son qilib berib boʻlmaydi. Avval uni toifa sifatida kodlaymiz.**
   *The same holds in AI: we cannot feed a city name to a model as a number. We first encode it as a category.*
   ▸ "Toshkent" → [1, 0, 0], "Samarqand" → [0, 1, 0]
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Qon guruhi, imtihondagi oʻrin va xonadagi harorat — har biri qaysi turga kiradi?**
    *Let's try it ourselves. Pause the video. Blood type, finishing place in an exam, and room temperature: which type is each?*
11. **Qon guruhi — nominal. Imtihondagi oʻrin — ordinal: birinchi ikkinchidan oldin, lekin oraliqlar teng emas. Harorat — uzluksiz.**
    *Blood type is nominal. Exam place is ordinal: first comes before second, but the gaps are not equal. Temperature is continuous.*
12. **Endi bizda olti yuzta maosh bor — sonli, uzluksiz maʼlumot. Lekin bu olti yuz kishi kim? Butun soha emas, uning bir qismi. Keyingi videoda shu haqida gaplashamiz.**
    *Now we have six hundred salaries: numerical, continuous data. But who are these six hundred people? Not the whole industry, only part of it. That is the next video.*

### Video 2 — Bosh toʻplam va tanlanma · Population and sample
1. **Assalomu alaykum, aziz doʻstlar. Bizda olti yuzta xodimning maoshi bor. Lekin bizni odatda kattaroq savol qiziqtiradi: butun sohada odamlar qancha maosh oladi?**
   *Hello, dear friends. We have the salaries of six hundred employees. But the question we usually care about is bigger: what do people earn across the whole industry?*
   ▸ the 600 dots, then the camera pulls back: they sit inside a huge faint cloud
2. **Sohadagi har bir xodimni oʻlchab chiqa olmaymiz — ular juda koʻp. Biz qiziqqan barcha birliklar toʻplamini bosh toʻplam deymiz.**
   *We cannot measure every employee in the industry; there are far too many. Every unit we care about is called the population.*
3. **Haqiqatda oʻlchagan qismimiz esa tanlanma deyiladi. Bizning olti yuzta maoshimiz — tanlanma.**
   *The part we actually measure is the sample. Our six hundred salaries are a sample.*
   ▸ labels "bosh toʻplam (population)" around the cloud, "tanlanma (sample)" around the 600
4. **Keling, kichikroq misol olaylik: beshta maosh, ming dollarda. Oʻttiz bir, qirq besh, qirq yetti, ellik ikki va sakson sakkiz.**
   *Let's take a smaller example: five salaries, in thousands of dollars. Thirty-one, forty-five, forty-seven, fifty-two, and eighty-eight.*
   ▸ five cards
5. **Ularni nomlash uchun har biriga raqam beramiz: x bir, x ikki, va hokazo x beshgacha. Tanlanma hajmini n bilan belgilaymiz, bu yerda n beshga teng.**
   *To name them, we number each one: x one, x two, and so on up to x five. We write the sample size as n; here n is five.*
   ▸ x₁ … x₅ appear under the cards, then "n = 5"
6. **Demak, x uch — uchinchi kuzatuv, qirq yetti. x besh esa sakson sakkiz.**
   *So x three is the third observation, forty-seven. And x five is eighty-eight.*
7. **Hammasini qoʻshish kerak boʻlsa, uzun yozib oʻtirmaymiz. Sigma belgisini ishlatamiz: i birdan n gacha, x i larning yigʻindisi.**
   *When we need to add them all up, we do not write it out longhand. We use the sigma sign: the sum of x i, for i from one to n.*
   ▸ x₁ + x₂ + x₃ + x₄ + x₅ folds into Σ xᵢ
8. **Bu yerda u ikki yuz oltmish uchga teng.**
   *Here that comes to two hundred and sixty-three.*
9. **Yana bitta kelishuv bor. Tanlanmadan hisoblangan sonlarni lotin harflari bilan yozamiz: x chiziqcha va s. Biz koʻra olmaydigan bosh toʻplamni esa grek harflari bilan: myu va sigma.**
   *One more convention. Numbers computed from the sample get Latin letters: x bar and s. The population we cannot see gets Greek letters: mu and sigma.*
   ▸ two columns under the cloud and the sample: x̄, s │ μ, σ
10. **Sunʼiy intellektda oʻqitish toʻplami — bu tanlanma. Model esa butun dunyo, yaʼni bosh toʻplam ustida ishlashi kerak. Kursimiz davomida bu farq qayta-qayta uchraydi.**
    *In AI, the training set is a sample. The model has to work on the whole world: the population. That gap comes back again and again in this course.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beshta maoshimizda x ikki qancha, va x bir qoʻshuv x besh nechaga teng?**
    *Let's try it ourselves. Pause the video. In our five salaries, what is x two, and what is x one plus x five?*
12. **x ikki — qirq besh. x bir qoʻshuv x besh — oʻttiz bir qoʻshuv sakson sakkiz, bir yuz oʻn toʻqqiz.**
    *x two is forty-five. x one plus x five is thirty-one plus eighty-eight: one hundred and nineteen.*
13. **Xoʻp, olti yuzta maoshimiz bor. Lekin olti yuzta sonning shaklini bir qarashda qanday koʻramiz? Keyingi videoda.**
    *So we have six hundred salaries. But how do we see the shape of six hundred numbers at a glance? That is the next video.*

### Video 3 — Gistogramma · The histogram
1. **Assalomu alaykum, aziz doʻstlar. Olti yuzta maoshni roʻyxat qilib yozsak, hech narsani koʻrmaymiz. Keling, ularning shaklini chizaylik.**
   *Hello, dear friends. Written as a list, six hundred salaries show us nothing. Let's draw their shape instead.*
   ▸ the salary list scrolls, then collapses into dots on an axis
2. **Maosh uzluksiz kattalik, shuning uchun deyarli hech bir qiymat takrorlanmaydi. Har bir qiymatni alohida sanasak, har biri bir martadan chiqadi.**
   *Salary is continuous, so almost no value repeats. If we count each value separately, every one of them appears exactly once.*
   ▸ 600 hair-thin bars, all the same height: 1
3. **Shuning uchun avval qiymatlarni sinflarga guruhlaymiz. Birinchi qadam — oraliq: eng kattasi bir yuz ellik bir ming, eng kichigi yigirma yetti ming. Oraliq bir yuz yigirma toʻrt ming dollar.**
   *So first we group the values into classes. Step one is the range: the largest is one hundred and fifty-one thousand, the smallest twenty-seven thousand. The range is one hundred and twenty-four thousand dollars.*
   ▸ min and max dots light up, a brace between them: $124,026
4. **Ikkinchi qadam: sinflar sonini tanlaymiz, odatda beshdan oʻngacha. Biz yettitasini olamiz.**
   *Step two: choose the number of classes, usually five to ten. We take seven.*
5. **Uchinchi qadam: kenglik. Oraliqni yettiga boʻlamiz — taxminan oʻn yetti ming yetti yuz. Qulay boʻlishi uchun yigirma ming dollargacha yaxlitlaymiz.**
   *Step three: the width. The range divided by seven is about seventeen thousand seven hundred. We round it up to a convenient twenty thousand dollars.*
   ▸ 124,026 ÷ 7 = 17,718 → 20,000; seven class edges drop onto the axis
6. **Toʻrtinchi qadam: har bir sinfga nechta odam tushishini sanaymiz.**
   *Step four: count how many people fall into each class.*
   ▸ dots fall into the seven classes; counts tick up: 156, 311, 89, 32, 7, 3, 2
7. **Qirq mingdan oltmish minggacha — uch yuz oʻn bir kishi, yarmidan koʻpi. Yuqoriga qarab esa ingichka dum choʻzilib ketadi.**
   *Forty to sixty thousand: three hundred and eleven people, more than half. Above that, a thin tail stretches out to the right.*
8. **Beshinchi qadam: har bir sinfga bitta ustun chizamiz va ustunlar bir-biriga tegib turadi. Chunki shkala uzluksiz: oraliq qoldirsak, goʻyo oʻsha maoshlar mavjud emasdek koʻrinadi.**
   *Step five: draw one bar per class, with the bars touching. The scale is continuous; a gap would suggest salaries that cannot exist.*
   ▸ the stacks become touching bars; a gap flashes red, then closes
9. **Mana bu — gistogramma. U bitta son koʻrsata olmaydigan narsani koʻrsatadi: maoshlar oʻngga qiyshaygan.**
   *This is a histogram. It shows what no single number can: the salaries are skewed to the right.*
10. **Sunʼiy intellektda ham yangi maʼlumot bilan birinchi ish shu: har bir belgining gistogrammasini chizamiz — qanday taqsimlangan, qayerda gʻalati qiymatlar bor.**
    *In AI, the first thing we do with a new dataset is the same: draw a histogram of every feature, to see how it is spread and where the strange values are.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Jadvaldan foydalanib, sakson mingdan koʻp oladigan xodimlar sonini topamiz.**
    *Let's try it ourselves. Pause the video. Using the table, we find how many employees earn more than eighty thousand.*
12. **Oxirgi toʻrtta sinfni qoʻshamiz: oʻttiz ikki, yetti, uch va ikki. Jami qirq toʻrt kishi.**
    *We add the last four classes: thirty-two, seven, three and two. Forty-four people in all.*
13. **Lekin rahbarimiz baribir bitta son soʻraydi. Qaysi son? Keyingi videoda.**
    *But our manager still asks for one number. Which one? That is the next video.*

### Video 4 — Oʻrtacha qiymat · The mean  *(already built — only the "you" lines change)*
- s1a: **…Rahbarimiz oddiy savol beradi…** · *…Our manager asks a simple question…*  (+ greeting at the start)
- s1b: **Olti yuzta sonni birma-bir oʻqib chiqa olmaymiz. Bizga… kerak.** · *We cannot read out six hundred numbers. We need…*
- s2a: **…Hammasini qoʻshamiz va teng boʻlib chiqamiz.** · *…We add everything up, and share it out equally.*
- s2c: **Keling, u aslida nima qilayotganini koʻraylik…** · *Let's look at what it is really doing…*
- s3a: **Shuning uchun umumiy yigʻindi muhim boʻlganda bizga aynan oʻrtacha qiymat kerak.** · *…the mean is what we want whenever totals matter.*
- s3b: **Uni olti yuzga koʻpaytirsak, butun ish haqi fondini qaytarib olamiz…** · *Multiply it back by six hundred, and we recover…*
- **new s3d (AI):** **Sunʼiy intellektda ham shunday: modelning xatosini butun maʼlumot boʻyicha oʻrtacha qilib olamiz va oʻqitish aynan shu sonni kamaytiradi.** · *AI works the same way: we average a model's error over the whole dataset, and training is exactly the job of shrinking that average.*  ▸ loss = (1/n) Σ errorᵢ
- s4a: **Endi uning qayerda pand berishini koʻraylik…** · *Now let's watch it fail…*
- s4b: **…Kutilganidek, ikkalasi bir-biriga yaqin.** · *…Close together, as we would expect.*
- s4e: **Keling, qizil chiziq qayerga tushganiga qaraylik…** · *Let's look at where that red line lands…*
- s5a: **Endi uzuq chiziqqa qaraylik…** · *Now let's look at the dashed line…*
- s6a: **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Mana toʻqqizta maosh, ming dollarda. Ularning oʻrtacha qiymatini hisoblaymiz. Keyin toʻqqiz kishidan nechtasi undan kam maosh olishini sanaymiz.** · *Let's try it ourselves. Pause the video. Here are nine salaries, in thousands of dollars. We work out the mean. Then we count how many of the nine earn less than it.*

### Video 5 — Mediana va moda · The median and the mode
1. **Assalomu alaykum, aziz doʻstlar. Oʻtgan videoda bitta milliarder oʻrtacha qiymatni boʻm-boʻsh joyga sudrab ketdi. Keling, bunga bardosh beradigan son topaylik.**
   *Hello, dear friends. In the last video, one billionaire dragged the mean into empty space. Let's find a number that holds its ground.*
2. **Gʻoya oddiy: maoshlarni kichigidan kattasiga qarab tizamiz va oʻrtada turgan odamni olamiz. Bu — mediana.**
   *The idea is simple: we line the salaries up from smallest to largest, and take the person standing in the middle. That is the median.*
3. **Beshta maosh: oʻttiz bir, qirq besh, qirq yetti, ellik ikki, sakson sakkiz. Ular tartiblangan, n beshga teng, demak oʻrtadagisi — uchinchisi, qirq yetti.**
   *Five salaries: thirty-one, forty-five, forty-seven, fifty-two, eighty-eight. They are sorted, n is five, so the middle one is the third: forty-seven.*
   ▸ five bars in a row; two from each end fade, the third glows
4. **Agar n juft boʻlsa-chi? Sakson sakkizni olib tashlaymiz. Endi toʻrtta qoldi va oʻrtada bitta emas, ikkita odam turibdi.**
   *What if n is even? Let's drop the eighty-eight. Now four are left, and there is not one middle person but two.*
5. **Bunday holda ikkalasining oʻrtachasini olamiz: qirq besh va qirq yetti — mediana qirq olti.**
   *Then we take the average of those two: forty-five and forty-seven, so the median is forty-six.*
6. **Endi beshtasiga qaytaylik. Ularning oʻrtacha qiymati ellik ikki butun oʻndan olti. Bu beshta maoshdan toʻrttasidan katta! Bitta sakson sakkiz uni yuqoriga tortib ketdi, mediana esa oʻrtadagi odamda qoldi.**
   *Back to the five. Their mean is fifty-two point six. That is larger than four of the five salaries! A single eighty-eight pulled it up, while the median stayed on the middle person.*
   ▸ red mean line at 52.6 above four bars; green median line on the third
7. **Demak, mediana tanlanmaning odatiy aʼzosini tasvirlaydi. Oʻrtacha qiymat esa yigʻindi teng boʻlinganda har kimga tegadigan ulushni.**
   *So the median describes a typical member of the sample. The mean describes each person's share if the total were split equally.*
8. **Shuning uchun davlat statistika idoralari xonadon daromadining medianasini eʼlon qiladi, uy narxlarini ham xuddi shunday. Bir nechta milliarder yoki saroy oʻrtachani maʼnosiz qilib qoʻyadi.**
   *That is why national statistics offices report median household income, and house prices the same way. A handful of billionaires or mansions would make the mean meaningless.*
9. **Yana bitta markaz bor: moda — eng koʻp uchraydigan qiymat. Kategorial maʼlumot uchun faqat u ishlaydi: eng keng tarqalgan qon guruhi yoki doʻkon eng koʻp sotadigan oyoq kiyim oʻlchami.**
   *There is one more center: the mode, the value that appears most often. It is the only one that works for categorical data: the most common blood type, or the shoe size a shop sells most.*
10. **Qoidamiz: simmetrik maʼlumot va yigʻindilar uchun — oʻrtacha qiymat. Qiyshiq maʼlumot va keskin qiymatlar uchun — mediana. Kategorial maʼlumot uchun — moda.**
    *Our rule of thumb: for symmetric data and for totals, the mean. For skewed data and extreme values, the median. For categorical data, the mode.*
    ▸ three cards, each with its data type icon
11. **Sunʼiy intellektda ham shunday: maʼlumotdagi bitta xato, masalan bitta ortiqcha nol bilan yozilgan maosh, oʻrtachani buzadi, medianani esa deyarli qimirlatmaydi. Shuning uchun maʼlumotni tozalashda koʻpincha medianaga tayanamiz.**
    *The same in AI: one error in the data, say a salary typed with an extra zero, wrecks the mean and barely moves the median. That is why data cleaning often leans on the median.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻtgan videodagi toʻqqizta maoshning medianasini topamiz.**
    *Let's try it ourselves. Pause the video. We find the median of the nine salaries from the last video.*
13. **Toʻqqizta qiymat, demak oʻrtadagisi beshinchisi: qirq yetti ming dollar. Oʻrtacha qiymat esa ellik ming uch yuz oʻttiz uch dollar edi.**
    *Nine values, so the middle one is the fifth: forty-seven thousand dollars. The mean was fifty thousand, three hundred and thirty-three.*
14. **Lekin markaz hamma narsani aytmaydi. Ikki xil maʼlumot bir xil oʻrtachaga ega boʻlib, butunlay boshqacha boʻlishi mumkin. Keyingi videoda.**
    *But a center does not tell the whole story. Two datasets can share the same mean and behave completely differently. That is the next video.*

### Video 6 — Dispersiya · Variance
1. **Assalomu alaykum, aziz doʻstlar. Tasavvur qilamiz, ishga ikki xil yoʻl bilan boramiz: avtobusda yoki mashinada. Besh kun avtobusda, besh kun mashinada vaqtni yozib boramiz.**
   *Hello, dear friends. Let's imagine we can get to work two ways: by bus or by car. We time five days by bus and five days by car.*
2. **Avtobus: oʻttiz, yigirma toʻqqiz, oʻttiz bir, oʻttiz, oʻttiz daqiqa. Mashina: oʻn sakkiz, qirq ikki, yigirma besh, oʻttiz besh, oʻttiz daqiqa.**
   *Bus: thirty, twenty-nine, thirty-one, thirty, thirty minutes. Car: eighteen, forty-two, twenty-five, thirty-five, thirty minutes.*
   ▸ two rows of dots on a minutes axis
3. **Ikkalasining oʻrtachasi ham roppa-rosa oʻttiz daqiqa. Faqat oʻrtachaga qarasak, ular bir xil.**
   *Both average exactly thirty minutes. If we only look at the mean, they are the same.*
4. **Lekin mashinada bir kuni oʻn ikki daqiqa kechikdik. Bizga yoyilishni oʻlchaydigan son kerak.**
   *But one day by car we were twelve minutes late. We need a number that measures spread.*
5. **Keling, har bir kunning oʻrtachadan farqini olaylik. Mashinada: minus oʻn ikki, plyus oʻn ikki, minus besh, plyus besh, nol.**
   *Let's take each day's distance from the mean. By car: minus twelve, plus twelve, minus five, plus five, zero.*
   ▸ arrows from the mean line to each car dot
6. **Ularni shunchaki qoʻshsak, nol chiqadi — musbatlar va manfiylar bir-birini yeb qoʻyadi. Shuning uchun har birini kvadratga oshiramiz.**
   *If we simply add them, we get zero: the pluses and minuses cancel. So we square each one first.*
   ▸ each arrow grows into a square: 144, 144, 25, 25, 0
7. **Kvadratlar yigʻindisi uch yuz oʻttiz sakkiz. Uni n minus birga, yaʼni toʻrtga boʻlamiz: sakson toʻrt butun oʻndan besh. Bu — dispersiya.**
   *The squares add up to three hundred and thirty-eight. We divide by n minus one, that is four: eighty-four point five. This is the variance.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Avtobusning dispersiyasini xuddi shu yoʻl bilan hisoblaymiz.**
   *Let's try it ourselves. Pause the video. We work out the bus's variance the same way.*
9. **Avtobusda farqlar atigi minus bir va plyus bir. Kvadratlar yigʻindisi ikki, dispersiya nol butun oʻndan besh.**
   *By bus the distances are only minus one and plus one. The squares add up to two, so the variance is zero point five.*
10. **Dispersiya kvadrat daqiqalarda oʻlchanadi — bu gʻalati birlik. Ildizdan chiqarsak, standart chetlanishni olamiz: mashinada taxminan toʻqqiz daqiqa, avtobusda bir daqiqadan kam.**
    *Variance is measured in squared minutes, which is an odd unit. Taking the square root gives the standard deviation: about nine minutes by car, less than one minute by bus.*
11. **Nima uchun n emas, n minus bir? Oʻrtachani tanlanmaning oʻzidan hisobladik, shuning uchun u tanlanmaga haqiqiy oʻrtachadan doim biroz yaqinroq turadi. n minus birga boʻlish shu kamchilikni tuzatadi.**
    *Why n minus one, not n? We computed the mean from the sample itself, so it always sits a little closer to the sample than the true mean does. Dividing by n minus one corrects for that.*
12. **Sunʼiy intellektda bir xil oʻrtacha aniqlikka ega ikki modeldan natijasi har safar sakrab turadiganini emas, barqarorini tanlaymiz. Bu farqni aynan dispersiya koʻrsatadi.**
    *In AI, between two models with the same average accuracy, we choose the steady one over the one that jumps around from run to run. Variance is what shows the difference.*
13. **Keyingi videoda dispersiya qanday qilib haqiqiy pul va chiqindiga aylanishini koʻramiz.**
    *In the next video, we see how variance turns into real money and real waste.*

### Video 7 — Yoyilish — bu xavf · Variance is risk
1. **Assalomu alaykum, aziz doʻstlar. Keling, ichimlik zavodiga boraylik. Shishada besh yuz millilitr deb yozilgan, qonun esa toʻrt yuz toʻqson beshdan besh yuz beshgacha ruxsat beradi.**
   *Hello, dear friends. Let's visit a bottling plant. The label says five hundred millilitres, and the law allows four hundred and ninety-five to five hundred and five.*
   ▸ a fill axis with the 495–505 band shaded
2. **Ikkita mashina bor, ikkalasi ham oʻrtacha roppa-rosa besh yuz millilitr quyadi.**
   *There are two machines, and both fill exactly five hundred millilitres on average.*
3. **Birinchi mashinaning standart chetlanishi ikki millilitr. Chegaralar oʻrtachadan ikki yarim standart chetlanish uzoqda, shuning uchun mingta shishadan atigi oʻn bittasi yaroqsiz.**
   *Machine A has a standard deviation of two millilitres. The limits sit two and a half standard deviations out, so only eleven bottles in a thousand are rejected.*
   ▸ a narrow bell inside the band; a grid of 1000 bottles, 11 turn red
4. **Ikkinchi mashinaning standart chetlanishi toʻrt millilitr. Endi xuddi shu chegaralar bor-yoʻgʻi bir butun toʻrtdan bir standart chetlanish uzoqlikda. Mingtadan ikki yuz oʻntasi yaroqsiz — har beshinchi shisha.**
   *Machine B has a standard deviation of four millilitres. Now the same limits are only one and a quarter standard deviations out. Two hundred and ten in a thousand are rejected: one bottle in five.*
   ▸ a wide bell spilling past the band; 210 of the 1000 turn red
5. **Yoyilish ikki baravar oshdi, chiqindi esa oʻn toʻqqiz baravar. Oʻrtacha qiymat esa bir millilitr ham qimirlamadi.**
   *The spread doubled, and the waste went up nineteen times. The mean never moved by a single millilitre.*
6. **Demak, zavod faqat oʻrtachani emas, yoyilishni boshqarishi kerak. Sifat nazoratidagi mashhur «Olti Sigma» gʻoyasi aynan shu.**
   *So the plant has to control the spread, not just the average. That is the whole idea behind Six Sigma quality control.*
7. **Kundalik hayotda ham shunday: jadvalga rioya qiladigan avtobus, kutish vaqti oldindan maʼlum klinika, haroratni ushlab turadigan pech. Oʻrtacha qiymat ishlar qanchalik tez-tez buzilishini hech qachon aytmaydi.**
   *Everyday life is the same: a bus that keeps its timetable, a clinic with predictable waiting times, an oven that holds its temperature. The average never tells us how often things go wrong.*
8. **Sunʼiy intellektda modelning bashorati bilan birga uning ishonchsizligini, yaʼni yoyilishini ham baholaymiz — shunda modelga qachon ishonmaslik kerakligini bilamiz.**
   *In AI, we estimate not just a model's prediction but its uncertainty, its spread, so we know when not to trust it.*
9. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Ikkinchi mashinaning yoyilishini kamaytira olmasak, oʻrtachani qayerga qoʻyish kerak?**
   *Let's think it through. Pause the video. If we cannot reduce machine B's spread, where should we set its average?*
10. **Aynan chegaralar oʻrtasida qoldiramiz. Oʻrtachani qaysi tomonga sursak ham, bir chegara yaqinlashadi va yaroqsiz shishalar koʻpayadi.**
    *Right in the middle of the limits. Whichever way we move the average, one limit gets closer, and more bottles are rejected.*
11. **Lekin dispersiya bitta keskin qiymatga juda sezgir. Chetga chiqqan qiymatlarga bardosh beradigan yoyilish oʻlchovi bormi? Keyingi videoda.**
    *But variance is very sensitive to a single extreme value. Is there a measure of spread that survives outliers? That is the next video.*

### Video 8 — Kvartillar va quti diagrammasi · Quartiles and box plots
1. **Assalomu alaykum, aziz doʻstlar. Mediana markazni chetga chiqqan qiymatlardan himoya qildi. Keling, yoyilish uchun ham xuddi shunday himoya quraylik.**
   *Hello, dear friends. The median protected the center from outliers. Let's build the same protection for spread.*
2. **Toʻqqizta maoshimizni tartiblab olamiz. Mediana — beshinchisi, qirq yetti. U maʼlumotni ikki yarmiga ajratadi.**
   *We take our nine salaries, sorted. The median is the fifth, forty-seven. It splits the data into two halves.*
   ▸ nine bars; the fifth glows and a divider drops
3. **Pastki yarmi: oʻttiz bir, oʻttiz sakkiz, qirq ikki, qirq besh. Uning medianasi oʻttiz sakkiz bilan qirq ikkining oʻrtachasi — qirq. Bu birinchi kvartil, Q bir.**
   *The lower half: thirty-one, thirty-eight, forty-two, forty-five. Its median is the average of thirty-eight and forty-two: forty. That is the first quartile, Q one.*
4. **Yuqori yarmi: qirq toʻqqiz, ellik ikki, oltmish bir, sakson sakkiz. Uning medianasi — ellik olti yarim. Bu uchinchi kvartil, Q uch.**
   *The upper half: forty-nine, fifty-two, sixty-one, eighty-eight. Its median is fifty-six and a half. That is the third quartile, Q three.*
5. **Endi beshta son maʼlumotni tasvirlaydi: eng kichigi, Q bir, mediana, Q uch va eng kattasi. Oʻttiz bir, qirq, qirq yetti, ellik olti yarim, sakson sakkiz.**
   *Now five numbers describe the data: the minimum, Q one, the median, Q three and the maximum. Thirty-one, forty, forty-seven, fifty-six and a half, eighty-eight.*
6. **Q uch minus Q bir — kvartillararo oraliq, IQR. U oʻrtadagi yarim maʼlumotning kengligi, bu yerda oʻn olti yarim. Medianaga oʻxshab, u keskin qiymatlarga bardosh beradi.**
   *Q three minus Q one is the interquartile range, the IQR: the width of the middle half of the data. Here, sixteen and a half. Like the median, it survives extreme values.*
7. **Endi keskin qiymatni aniqlaymiz. Q uchga bir yarim IQR qoʻshamiz: sakson bir butun yuzdan yigirma besh. Bundan yuqoridagi har qanday qiymat chetga chiqqan hisoblanadi.**
   *Now we can flag outliers. Add one and a half IQRs to Q three: eighty-one point two five. Anything above that counts as an outlier.*
8. **Sakson sakkiz bu chegaradan oshib ketdi. Demak, sakson sakkiz ming dollarlik maosh — chetga chiqqan qiymat.**
   *Eighty-eight is past that fence. So the eighty-eight thousand dollar salary is flagged as an outlier.*
9. **Bularning hammasini bitta rasmda chizamiz: Q birdan Q uchgacha quti, ichida mediana chizigʻi, moʻylovlar va alohida nuqta — chetga chiqqan qiymat. Bu quti diagrammasi.**
   *We draw all of this as one picture: a box from Q one to Q three, a median line inside, whiskers, and a separate dot for the outlier. This is a box plot.*
   ▸ the nine bars turn sideways and collapse into the box plot
10. **Uning kuchi — guruhlarni solishtirishda. Xizmat koʻrsatish markazining uchta filialidagi kutish vaqtlari: A filialida mediana oʻn bir butun oʻndan sakkiz daqiqa, B filialida oʻn yetti butun oʻndan yetti, C filialida yigirma toʻqqiz yarim.**
    *Its strength is comparing groups. Waiting times at three branches of a service centre: branch A has a median of eleven point eight minutes, branch B seventeen point seven, branch C twenty-nine point five.*
    ▸ three box plots side by side
11. **C filiali eng sekin va eng beqaror: uning qutisi deyarli yigirma daqiqa keng. Bitta oʻrtacha son qaysi filialni tuzatish kerakligini koʻrsatmas edi.**
    *Branch C is both the slowest and the most variable: its box is almost twenty minutes wide. A single average would not tell us which branch to fix.*
12. **Sunʼiy intellektda modelni oʻqitishdan oldin aynan shu qoida bilan gʻalati qiymatlarni topamiz: notoʻgʻri yozilgan yozuvlar, sensor xatolari.**
    *In AI, before training a model we use exactly this rule to catch strange values: mistyped records, sensor glitches.*
13. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Pastki chegarani, yaʼni Q bir minus bir yarim IQR ni hisoblaymiz. Undan pastda qiymat bormi?**
    *Let's try it ourselves. Pause the video. We work out the lower fence, Q one minus one and a half IQRs. Is any value below it?*
14. **Pastki chegara oʻn besh butun yuzdan yigirma besh. Eng kichik maosh oʻttiz bir, demak pastda chetga chiqqan qiymat yoʻq.**
    *The lower fence is fifteen point two five. The smallest salary is thirty-one, so there is no outlier at the bottom.*
15. **Lekin hatto beshta son ham aldashi mumkin. Keyingi videoda statistikasi bir xil, lekin rasmi butunlay boshqacha boʻlgan toʻrtta maʼlumotni koʻramiz.**
    *But even five numbers can fool us. In the next video, four datasets with the same statistics and completely different pictures.*

### Video 9 — Maʼlumotni doim chizamiz · Always plot the data (Anscombe)
1. **Assalomu alaykum, aziz doʻstlar. Keling, toʻrtta maʼlumotlar toʻplamini olaylik. Har birida oʻn bitta nuqta bor.**
   *Hello, dear friends. Let's take four datasets. Each has eleven points.*
   ▸ four tables of numbers, no plots yet
2. **Ularning statistikasini hisoblaymiz. x ning oʻrtachasi toʻrttasida ham toʻqqiz. y ning oʻrtachasi toʻrttasida ham yetti yarim.**
   *Let's compute their statistics. The mean of x is nine in all four. The mean of y is seven and a half in all four.*
3. **x ning dispersiyasi hammasida oʻn bir. Korrelyatsiya hammasida taxminan nol butun sakkiz yuz oʻn olti. Hatto eng yaxshi toʻgʻri chiziq ham bir xil: y teng uch qoʻshuv x ning yarmi.**
   *The variance of x is eleven in all of them. The correlation is about zero point eight one six in all of them. Even the best-fitting line is the same: y equals three plus half of x.*
4. **Raqamlarga qarasak, toʻrttasi bir xil maʼlumot. Xoʻp, endi ularni chizaylik.**
   *By the numbers, these are the same dataset four times. Now let's draw them.*
5. **Birinchisi: oddiy chiziqli bogʻlanish, atrofida biroz tarqoqlik. Toʻgʻri chiziq bu yerda oʻrinli.**
   *The first: an ordinary straight-line relationship with some scatter. Here, a line fits.*
6. **Ikkinchisi: mukammal egri chiziq. Bu yerda toʻgʻri chiziq umuman notoʻgʻri model.**
   *The second: a perfect curve. Here, a straight line is the wrong model entirely.*
7. **Uchinchisi: mukammal toʻgʻri chiziq, lekin bitta chetga chiqqan nuqta qiyalikni oʻziga tortib ketgan.**
   *The third: a perfect line, but one outlier pulls the fitted slope toward itself.*
8. **Toʻrtinchisi: hech qanday bogʻlanish yoʻq. Faqat bitta uzoqdagi nuqta kuchli korrelyatsiyani soxtalashtiryapti.**
   *The fourth: no relationship at all. A single far-off point fakes a strong correlation.*
9. **Statistik Frensis Enskomb bu toʻrt toʻplamni ming toʻqqiz yuz yetmish uchinchi yilda aynan shu maqsadda eʼlon qilgan: maʼlumotni chizmasdan turib statistikaga ishonmang.**
   *The statistician Francis Anscombe published these four datasets in nineteen seventy-three for exactly this reason: never trust the statistics without plotting the data.*
10. **Sunʼiy intellektda bu juda muhim: aniqlik kabi bitta son model toʻgʻri tanlanganini aytmaydi. Modelga ishonishdan oldin uning nuqtalari va xatolarini doim chizamiz.**
    *In AI this matters a lot: one number like accuracy does not tell us the model is the right one. Before we trust a model, we always plot its points and its errors.*
11. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Toʻrttasidan qaysi birida toʻgʻri chiziqli model haqiqatan oʻrinli?**
    *Let's think it through. Pause the video. In which of the four is a straight-line model actually right?*
12. **Faqat birinchisida. Qolgan uchtasida bir xil chiziq bizni aldaydi.**
    *Only the first. In the other three, the same line misleads us.*
13. **Mana shu bilan maʼruzamizning birinchi qismini tugatamiz. Keyingi qismda noaniqlikni oʻlchashni oʻrganamiz: ehtimollik.**
    *That brings us to the end of the first part of this lecture. In the next part we learn to measure uncertainty: probability.*

---

## Part 1 — Ehtimollik

### Video 10 — Namunalar fazosi, hodisa, ehtimollik · Sample space, event, probability
1. **Assalomu alaykum, aziz doʻstlar. Maʼruzamizning ikkinchi qismiga xush kelibsiz. Ertaga yomgʻir yogʻadimi? Kubik oltini koʻrsatadimi? Keling, bunday savollarni songa aylantirishni oʻrganaylik.**
   *Hello, dear friends, and welcome to the second part of our lecture. Will it rain tomorrow? Will the die show a six? Let's learn to turn questions like these into numbers.*
2. **Birinchi qadam: qarashdan oldin, sodir boʻlishi mumkin boʻlgan hamma narsani yozib chiqamiz. Kubik uchun bu bir, ikki, uch, toʻrt, besh, olti. Buni namunalar fazosi deymiz va omega bilan belgilaymiz.**
   *Step one: before we look, we write down everything that could happen. For a die, that is one, two, three, four, five, six. We call this the sample space, and write it as omega.*
   ▸ six die faces drop into a set Ω
3. **Tanga uchun: gerb yoki raqam. Ertangi kun uchun: yomgʻir yogʻadi yoki yogʻmaydi.**
   *For a coin: heads or tails. For tomorrow: rain or no rain.*
4. **Ikkinchi qadam: savolimizni yozamiz. Kubik juft son koʻrsatadimi? Javobi «ha» boʻladigan natijalarni yigʻamiz: ikki, toʻrt, olti. Bu toʻplam hodisa deyiladi.**
   *Step two: we write down our question. Will the die show an even number? We collect the outcomes that answer yes: two, four, six. That set is called an event.*
   ▸ 2, 4, 6 lift out of Ω into a ring labelled A
5. **Uchinchi qadam: har bir hodisaga noldan birgacha bitta son beramiz. Nol — mumkin emas, bir — aniq. Omega ehtimoli doim bir, chunki nimadir albatta sodir boʻladi.**
   *Step three: we give each event one number between zero and one. Zero means impossible, one means certain. The probability of omega is always one, because something must happen.*
6. **Toʻgʻri kubikda juft son chiqish ehtimoli: oltita natijadan uchtasi, yaʼni ikkidan bir.**
   *For a fair die, the probability of an even number is three outcomes out of six: one half.*
7. **Nima uchun toʻplamlar bilan ovora boʻlamiz? Chunki savol toʻplamga aylangach, «yoki» birlashmaga, «va» kesishmaga, «emas» toʻldiruvchiga aylanadi. Hisoblashni esa qoidalar bajaradi.**
   *Why bother with sets? Because once a question is a set, "or" becomes a union, "and" becomes an intersection, and "not" becomes a complement. Then the rules do the counting for us.*
8. **Sunʼiy intellektda klassifikator aynan shunday ishlaydi: har bir sinf uchun noldan birgacha ehtimol chiqaradi va ularning yigʻindisi birga teng.**
   *In AI, a classifier works exactly like this: it outputs a probability between zero and one for each class, and they add up to one.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Kubik toʻrtdan katta son koʻrsatadi» hodisasini yozamiz va uning ehtimolini topamiz.**
   *Let's try it ourselves. Pause the video. We write down the event "the die shows more than four", and find its probability.*
10. **Besh va olti. Oltitadan ikkitasi, yaʼni uchdan bir.**
    *Five and six. Two out of six: one third.*
11. **Keyingi videoda bu ehtimollarni birlashtiradigan uchta qoidani koʻramiz.**
    *In the next video, the three rules that combine these probabilities.*

### Video 11 — Uchta qoida · The three rules
1. **Assalomu alaykum, aziz doʻstlar. Bizda oddiy hodisalarning ehtimollari bor. Murakkab hodisalarnikini qanday topamiz? Buning uchun uchta qoida yetarli.**
   *Hello, dear friends. We have the probabilities of simple events. How do we get them for complicated ones? Three rules are enough.*
2. **Birinchisi — toʻldiruvchi qoidasi. A sodir boʻlmasligi ehtimoli bir minus A ning ehtimoli. Juft son chiqmasligi: bir minus ikkidan bir, yaʼni ikkidan bir.**
   *The first is the complement rule. The probability that A does not happen is one minus the probability of A. Not even: one minus a half, which is a half.*
3. **U «hech boʻlmaganda bittasi» kabi savollarda juda qulay: hech biri boʻlmasligini hisoblab, birdan ayiramiz.**
   *It is the easy way into "at least one" questions: we work out "none", and subtract it from one.*
4. **Ikkinchisi — qoʻshish qoidasi. Keling, ellik ikkita kartadan bittasini olaylik. Yurak belgili karta chiqishi: ellik ikkidan oʻn uch. Qirol chiqishi: ellik ikkidan toʻrt.**
   *The second is the addition rule. Let's draw one card from fifty-two. A heart: thirteen out of fifty-two. A king: four out of fifty-two.*
   ▸ the 52-card grid; the hearts row and the kings column light up
5. **Yurak yoki qirol chiqishi ehtimoli-chi? Oʻn uch qoʻshuv toʻrt emas. Yurak qiroli ikkala guruhda ham bor — uni ikki marta sanab qoʻyamiz.**
   *What about a heart or a king? Not thirteen plus four. The king of hearts is in both groups; we would count it twice.*
   ▸ the crossing card flashes
6. **Shuning uchun kesishmani bir marta ayiramiz: oʻn uch qoʻshuv toʻrt minus bir — ellik ikkidan oʻn olti.**
   *So we subtract the overlap once: thirteen plus four minus one, sixteen out of fifty-two.*
7. **Uchinchisi — koʻpaytirish qoidasi. A va B birga sodir boʻlishi ehtimoli: A ning ehtimoli koʻpaytiruv A sodir boʻlgandagi B ning ehtimoli.**
   *The third is the multiplication rule. The probability of A and B together is the probability of A, times the probability of B given that A has happened.*
8. **Yurak qiroli: avval yurak chiqishi, ellik ikkidan oʻn uch. Yurak chiqqanini bilsak, uning qirol boʻlishi oʻn uchdan bir. Koʻpaytirsak — ellik ikkidan bir.**
   *The king of hearts: first a heart, thirteen out of fifty-two. Given it is a heart, the chance it is a king is one in thirteen. Multiply them: one out of fifty-two.*
9. **«Berilgan» degan bu tushuncha — shartli ehtimollik. Uni ikkinchi maʼruzada chuqur oʻrganamiz.**
   *That word "given" is conditional probability. We study it in depth in Lecture 2.*
10. **Sunʼiy intellektda til modeli gapni aynan koʻpaytirish qoidasi bilan baholaydi: har bir soʻzning ehtimolini oldingi soʻzlar berilganda hisoblab, hammasini koʻpaytiradi.**
    *In AI, a language model scores a sentence with exactly the multiplication rule: the probability of each word given the words before it, all multiplied together.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Karta yurak ham, qirol ham boʻlmasligi ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. What is the probability that the card is neither a heart nor a king?*
12. **Toʻldiruvchi qoidasi: bir minus ellik ikkidan oʻn olti, yaʼni ellik ikkidan oʻttiz olti.**
    *The complement rule: one minus sixteen out of fifty-two, which is thirty-six out of fifty-two.*
13. **Keyingi videoda toʻldiruvchi qoidasi deyarli hammani aldaydigan savolga javob beradi.**
    *In the next video, the complement rule answers a question that fools almost everyone.*

### Video 12 — Tugʻilgan kun masalasi · The birthday problem
1. **Assalomu alaykum, aziz doʻstlar. Xonada nechta odam boʻlsa, ikkitasining tugʻilgan kuni bir xil boʻlish ehtimoli yarimdan oshadi? Koʻpchilik yuz sakson atrofida deb oʻylaydi.**
   *Hello, dear friends. How many people must be in a room before the chance that two share a birthday passes one half? Most people guess around one hundred and eighty.*
2. **Keling, toʻgʻridan-toʻgʻri sanab koʻraylik: kimdir kim bilandir bir kunda tugʻilgan barcha holatlar. Juftlar, uchliklar, bir nechta juftlar — sanash tezda chalkashib ketadi.**
   *Let's try to count it directly: every case where someone shares a birthday with someone. Pairs, triples, several pairs at once; the counting gets messy fast.*
3. **Shuning uchun teskarisini hisoblaymiz: hammaning tugʻilgan kuni har xil. Keyin uni birdan ayiramiz.**
   *So we compute the opposite: everyone's birthday is different. Then we subtract it from one.*
4. **Birinchi odam istalgan kunda tugʻilishi mumkin. Ikkinchisi qolgan uch yuz oltmish toʻrt kundan birida boʻlishi kerak. Uchinchisi — uch yuz oltmish uch kundan birida, va hokazo.**
   *The first person can have any birthday. The second must land on one of the other three hundred and sixty-four days. The third on one of three hundred and sixty-three, and so on.*
   ▸ a 365-cell calendar; each new person takes a free cell
5. **Bu kasrlarni koʻpaytiramiz va natijani birdan ayiramiz.**
   *We multiply those fractions together, and subtract the result from one.*
6. **Oʻn kishida ehtimol atigi oʻn ikki foiz. Yigirma uch kishida esa ellik butun oʻndan yetti foiz. Yarimdan oshdi!**
   *With ten people the chance is only twelve percent. With twenty-three, it is fifty point seven percent. Past one half!*
   ▸ the curve draws itself point by point; a marker stops at 23
7. **Ellik kishida — toʻqson yetti foiz, yetmish kishida esa deyarli aniq.**
   *With fifty people, ninety-seven percent. With seventy, almost certain.*
8. **Nima uchun sezgimiz adashadi? Chunki biz oʻzimizni boshqalar bilan solishtiramiz. Aslida esa har bir juftlik hisobga kiradi: yigirma uch kishida ikki yuz ellik uchta juftlik bor.**
   *Why does our intuition fail? Because we compare ourselves with the others. In fact every pair counts: twenty-three people make two hundred and fifty-three pairs.*
   ▸ 23 dots, then all 253 connecting lines
9. **Kompyuter fanlari va sunʼiy intellektda xuddi shu hisob xesh toʻqnashuvlari va maʼlumotdagi takrorlanishlarni baholaydi: ular kutganimizdan ancha tez paydo boʻladi.**
   *In computing and AI, the same calculation estimates hash collisions and duplicates in data: they show up much sooner than we expect.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻttiz kishilik sinfda ehtimol qancha? Grafikdan topamiz.**
    *Let's try it ourselves. Pause the video. In a class of thirty, what is the chance? Let's read it off the curve.*
11. **Taxminan yetmish bir foiz. Oʻttiz kishilik sinflarning koʻpchiligida tugʻilgan kuni bir xil juftlik bor.**
    *About seventy-one percent. Most classes of thirty have a shared birthday.*
12. **Bu hisobda biz odamlarning tugʻilgan kunlari bir-biriga bogʻliq emas deb oldik. «Bogʻliq emas» aslida nimani anglatadi? Keyingi videoda.**
    *In that calculation we assumed people's birthdays have nothing to do with each other. What does that really mean? That is the next video.*

### Video 13 — Istisno qiluvchi va erkli hodisalar · Mutually exclusive vs. independent
1. **Assalomu alaykum, aziz doʻstlar. Ikki tushuncha koʻpincha adashtiriladi: bir-birini istisno qiluvchi va erkli hodisalar. Keling, farqini kubikda koʻraylik.**
   *Hello, dear friends. Two ideas get mixed up all the time: mutually exclusive and independent. Let's see the difference on a die.*
2. **Ikki hodisa hech qachon birga sodir boʻlmasa, ular bir-birini istisno qiladi: kesishmasi boʻsh, birga sodir boʻlish ehtimoli nol.**
   *Two events are mutually exclusive if they can never happen together: their overlap is empty, and the probability of both is zero.*
3. **Ikki hodisa erkli, agar birga sodir boʻlish ehtimoli ehtimollar koʻpaytmasiga teng boʻlsa. Boshqacha aytganda, birini bilish ikkinchisi haqida hech narsa aytmaydi.**
   *Two events are independent if the probability of both equals the product of their probabilities. In other words, knowing one tells us nothing about the other.*
4. **Kubik tashlaymiz. A — juft son: ikki, toʻrt, olti, ehtimoli ikkidan bir. B — toʻrtdan katta: besh, olti, ehtimoli uchdan bir.**
   *We roll a die. A is "even": two, four, six, with probability one half. B is "more than four": five, six, with probability one third.*
   ▸ Venn diagram over the six faces
5. **Ikkalasi birga: faqat olti, ehtimoli oltidan bir. Ikkidan bir koʻpaytiruv uchdan bir ham oltidan bir. Demak, A va B erkli.**
   *Both together: only six, with probability one sixth. And one half times one third is also one sixth. So A and B are independent.*
6. **Lekin ular bir-birini istisno qilmaydi — olti ikkalasida ham bor.**
   *But they are not mutually exclusive: six belongs to both.*
7. **Xoʻp, endi teskarisini olaylik: juft va toq. Ular bir-birini istisno qiladi. Erklimi?**
   *Now the reverse: even and odd. They are mutually exclusive. Are they independent?*
8. **Yoʻq! Son juft chiqqanini bilsak, toq emasligini aniq bilamiz — bu kuchli bogʻliqlik. Ehtimollar koʻpaytmasi toʻrtdan bir, haqiqiy ehtimol esa nol.**
   *No! If we know the number came up even, we know for certain it is not odd. That is strong dependence. The product of the probabilities is one quarter, but the real probability is zero.*
9. **Qoida: ehtimoli noldan katta boʻlgan ikki istisno qiluvchi hodisa har doim bogʻliq.**
   *The rule: two mutually exclusive events with nonzero probability are always dependent.*
10. **Sunʼiy intellektda mashhur sodda Bayes klassifikatori aynan erklilik farazi ustiga qurilgan: u har bir soʻzni boshqalaridan erkli deb hisoblaydi.**
    *In AI, the well-known naive Bayes classifier is built on exactly this assumption: it treats each word as independent of the others.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Juft son» va «uchdan kichik son» hodisalari erklimi?**
    *Let's try it ourselves. Pause the video. Are the events "even" and "less than three" independent?*
12. **Kesishmasi faqat ikki, oltidan bir. Ikkidan bir koʻpaytiruv uchdan bir ham oltidan bir. Demak, erkli.**
    *Their overlap is only two: one sixth. One half times one third is also one sixth. So they are independent.*
13. **Hozirgacha biz toʻgʻri kubikda sanadik. Lekin real dunyoda teng ehtimolli natijalar kamdan-kam uchraydi. Keyingi videoda.**
    *So far we have counted on a fair die. But in the real world, equally likely outcomes are rare. That is the next video.*

### Video 14 — Klassik va empirik ehtimollik · Classical vs. empirical probability
1. **Assalomu alaykum, aziz doʻstlar. Ob-havo maʼlumotida eshitamiz: ertaga yomgʻir yogʻish ehtimoli yetmish foiz. Bu son qayerdan keladi?**
   *Hello, dear friends. The weather forecast says: seventy percent chance of rain tomorrow. Where does that number come from?*
2. **Kubikda biz klassik ehtimollikdan foydalandik: barcha natijalar teng ehtimolli boʻlsa, hodisadagi natijalar sonini jami natijalar soniga boʻlamiz.**
   *On the die, we used classical probability: when all outcomes are equally likely, we divide the outcomes in the event by the total number of outcomes.*
3. **Ob-havoda esa teng ehtimolli natijalar yoʻq. Sanaydigan fazomiz ham yoʻq.**
   *Weather has no equally likely outcomes. There is no sample space to count.*
4. **Buning oʻrniga oʻtmishga qaraymiz: bugungidek sharoitdagi barcha oʻtgan kunlarning taxminan yetmish foizida yomgʻir yoqqan. Bu — empirik ehtimollik.**
   *Instead, we look at the past: of all past days with conditions like today's, it rained on about seventy percent. That is empirical probability.*
   ▸ a grid of past days filling with rain/no-rain icons (labelled as an illustration)
5. **Formula oddiy: hodisa kuzatilgan holatlar sonini jami kuzatuvlar soniga boʻlamiz.**
   *The formula is simple: the number of times the event was observed, divided by the total number of observations.*
6. **Masalan, olti yuzta xodimimizdan uch yuz oʻn bittasi qirq mingdan oltmish minggacha oladi. Tasodifiy xodimning shu oraliqda boʻlishining empirik ehtimoli — taxminan ellik ikki foiz.**
   *For example, of our six hundred employees, three hundred and eleven earn between forty and sixty thousand. The empirical probability that a random employee lands there is about fifty-two percent.*
   ▸ the histogram from video 3; the 40–60k bar lifts out: 311 / 600
7. **Sunʼiy intellekt deyarli har doim empirik ehtimollikka tayanadi: oʻqitish toʻplamidagi sinflar ulushi, matnlardagi soʻzlar chastotasi, reklamalarni bosishlar ulushi.**
   *AI almost always relies on empirical probability: class shares in a training set, word frequencies in a corpus, click-through rates in logs.*
8. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Spam filtrini toʻqson foizi spam boʻlgan maʼlumotda oʻqitdik. Shu maʼlumotdan olingan spam ehtimoli haqiqiy pochtaga mos keladimi?**
   *Let's think it through. Pause the video. We trained a spam filter on data where ninety percent of emails are spam. Is the spam probability from that data right for real email?*
9. **Yoʻq. Empirik ehtimollik faqat maʼlumot olingan joy uchun toʻgʻri. Tanlanma bosh toʻplamga oʻxshamasa, ehtimol ham adashadi.**
   *No. An empirical probability is only right for the place the data came from. If the sample does not look like the population, the probability is wrong too.*
10. **Keling, maʼruzani yakunlaylik. Maʼlumot turi qaysi hisob toʻgʻri ekanini belgilaydi. Oʻrtacha qiymat yigʻindini eslab qoladi, mediana chetga chiqqan qiymatlarga bardosh beradi. Dispersiya va IQR xavfni oʻlchaydi. Maʼlumotni doim chizamiz. Ehtimollik qoidalari esa murakkab hodisalarni oddiylaridan hisoblaydi.**
    *Let's wrap up the lecture. The type of data decides which calculations are valid. The mean remembers the total; the median survives outliers. Variance and the IQR measure risk. We always plot the data. And the probability rules build complex events from simple ones.*
11. **Mana shu bilan birinchi maʼruzamizni tugatamiz. Keyingi maʼruzada «berilgan» soʻzining kuchini koʻramiz: shartli ehtimollik va Bayes teoremasi.**
    *That brings our first lecture to an end. In the next lecture, we see the power of the word "given": conditional probability and Bayes' theorem.*
