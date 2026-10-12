# Lecture 1 — video narration (draft 4, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Berilganlar va tavsiflovchi statistika) =
sections 1–9, Part 1 (Ehtimollik) = sections 10–14. A part card opens each part and a short section card
("3-boʻlim · Gistogramma") opens each section. Each section: problem first → concept as the answer → one AI use →
a hands-on pause → the question the next section answers.

**Draft 4 (only the new lines need approval):** each concept explained from more than one side, and earlier ideas
recapped before they are used (instructor, after Lecture 4). New lines carry a letter after the number (**5a**, **8b**;
in section 4, **s2d** and **s3e**); every approved line is unchanged. The added angles: why averaging ordinal codes
misleads; digits that are not numbers (postcodes); a sample must look like its population; x̄ is what we compute, μ
what we want; choosing the number of classes; reading a histogram's shape; the mean as a balance point and as a
formula; the middle position (n + 1)/2; mean above median means a right tail; why squares and not absolute values;
the standard deviation as a typical distance; limits measured in standard deviations; quartiles as quarters; why the
IQR ignores one huge value; what correlation is (ahead of Lecture 9); probability as a long-run share (three evens in
a row is ordinary); the complement and multiplication rules together (at least one six in four rolls); the overlap as
two circles; the birthday product written out; independence on a coin and a die; exclusive is a picture, independent
is a number; empirical shares settle as observations grow. New numbers: `capture_l01.py`, tested in `test_l01.py`.

**Draft 3:** one video per lecture — a single greeting and lecture intro, "keyingi/avvalgi boʻlim" instead of
"keyingi/oʻtgan video", part transitions inside the video. **Draft 2:** data = **berilganlar** (maʼlumot only where *information* is meant, e.g. "ob-havo maʼlumoti");
descriptive = **tavsiflovchi**; every Uzbek line rewritten as spoken Uzbek in your phrasing instead of a translation
of the English ("Toshkent qoʻshuv Samarqand, va boʻlamiz ikkiga"). Spread = *tarqoqlik*.

**Voice:** "we", never "you" — the only line addressed to the viewer is *Videoni toʻxtating* on the pause card.
**Numbers:** every figure comes from `video/statistics/raw/l01_numbers.json` / `l01_figures.txt`
(`capture_l01.py`, asserted against the slides). Narration spells them; the screen shows digits.

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "1-maʼruza" → learning goals
0. **Assalomu alaykum, aziz doʻstlar. Birinchi maʼruzamizga xush kelibsiz. Bu maʼruza ikki qismdan iborat. Nolinchi qismda berilganlar va tavsiflovchi statistikani oʻrganamiz, birinchi qismda esa ehtimollikni.**
   *Hello, dear friends, and welcome to our first lecture. It has two parts. In part zero we study data and descriptive statistics, and in part one, probability.*

## Part 0 — Berilganlar va tavsiflovchi statistika
▸ part card "0-qism · Berilganlar va tavsiflovchi statistika"

### 1-boʻlim · Section 1 — Berilganlar turlari · Data types
1. **Keling, boshladik. Statistikada birinchi savol hisob-kitob emas. Avval qoʻlimizdagi berilganlar qanday turda ekanini bilib olishimiz kerak.**
   *Let's begin. In statistics, the first question is not a calculation. The first question is: what kind of data do we have?*
   ▸ six cards drop in: koʻz rangi · tugʻilgan shahar · baho · farzandlar soni · maosh · boʻy
2. **Tasavvur qilamiz, ikki kishining tugʻilgan shahrini olib, oʻrtachasini hisoblamoqchimiz. Toshkent qoʻshuv Samarqand, va boʻlamiz ikkiga. Bunday hisobning hech qanday maʼnosi yoʻq.**
   *Let's imagine we add up two people's cities of birth and divide by two. Tashkent plus Samarkand, divided by two. That means nothing.*
   ▸ "(Toshkent + Samarqand) ÷ 2 = ?" then a red cross
3. **Demak, ayrim berilganlar son emas, balki toifa boʻladi. Bunday berilganlar kategorial berilganlar deyiladi.**
   *So some data are not numbers at all, but categories. We call them categorical data.*
   ▸ screen splits: left bin "kategorial", right bin "sonli"
4. **Koʻz rangi yoki tugʻilgan shaharni hech qanday tartibga solib boʻlmaydi. Bular nominal berilganlar.**
   *Eye colour and city of birth have no natural order. That is nominal data.*
   ▸ two cards slide into "nominal", shuffled freely
5. **Baho esa past, oʻrta, yuqori boʻladi. Mana bu yerda tartib bor, lekin ular orasidagi masofa teng emas. Bunday berilganlar tartibli, yaʼni ordinal deyiladi.**
   *A rating of low, medium, high does have an order, but the steps are not equal. That is ordinal data.*
   ▸ past → oʻrta → yuqori on a line with unequal gaps
5a. **Ordinal toifalarni songa aylantirsak ham, masalan past — bir, oʻrta — ikki, yuqori — uch deb yozsak ham, ular orasidagi masofa baribir teng boʻlib qolmaydi. Shuning uchun bunday sonlarning oʻrtachasiga ehtiyot boʻlib qaraymiz.**
   *Even if we turn ordinal categories into numbers, writing low as one, medium as two and high as three, the gaps between them do not become equal. So we treat an average of such numbers with care.*
   ▸ past · oʻrta · yuqori relabelled 1 · 2 · 3, the unequal gaps still drawn under them
6. **Xoʻp, endi sonli berilganlarga oʻtaylik. Farzandlar sonini sanaymiz: bitta, ikkita, uchta. Ikki yarimta farzand boʻlmaydi. Bular diskret berilganlar.**
   *Now let's move to numerical data. We count children: one, two, three. There is no such thing as two and a half children. That is discrete data.*
   ▸ number line, dots only on whole numbers; 2.5 crossed out
7. **Maosh yoki boʻy esa oʻlchanadi va oraliqdagi istalgan qiymatni olishi mumkin. Bular uzluksiz berilganlar.**
   *Salary and height are measured on a scale, and can take any value in between. That is continuous data.*
   ▸ a marker glides along a ruler: 172 → 172.4 → 172.43
8. **Bu nima uchun kerak? Chunki berilganlar turiga qarab qaysi hisob toʻgʻri ekanini bilamiz. Oʻrtacha qiymat va standart chetlanishni faqat sonli berilganlar uchun hisoblaymiz. Kategorial berilganlarni esa sanaymiz va ulushini topamiz.**
   *Why does this matter? Because the type of data decides which calculations make sense. A mean or a standard deviation only means something for numerical data. Categorical data we count, and turn into proportions.*
   ▸ the 2×2 map, "sanash, ulush" under categorical and "oʻrtacha, chetlanish" under numerical
8a. **Eʼtibor beraylik: son bilan yozilgan hamma narsa ham sonli berilgan emas. Telefon raqami yoki pochta indeksining oʻrtachasi Toshkent bilan Samarqandning oʻrtachasi kabi maʼnosiz. Tekshirish oson: bu sonlarni qoʻshishning maʼnosi bormi?**
   *Note that not everything written in digits is numerical data. The average of phone numbers or postcodes is as meaningless as the average of Tashkent and Samarkand. The test is simple: does adding these numbers mean anything?*
   ▸ a postcode card and a phone-number card slide into the categorical bin
8b. **Demak, toʻrtta tur bor: nominal va ordinal — kategorial berilganlar, diskret va uzluksiz — sonli berilganlar.**
   *So there are four types: nominal and ordinal are categorical data, discrete and continuous are numerical data.*
   ▸ the 2×2 map, all six cards in their cells
9. **Sunʼiy intellektda ham xuddi shunday. Shahar nomini modelga son qilib berolmaymiz, avval uni toifa sifatida kodlab olamiz.**
   *The same holds in AI: we cannot feed a city name to a model as a number. We first encode it as a category.*
   ▸ "Toshkent" → [1, 0, 0], "Samarqand" → [0, 1, 0]
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Qon guruhi, imtihondagi oʻrin va xonadagi harorat — har biri qaysi turga kiradi?**
    *Let's try it ourselves. Pause the video. Blood type, finishing place in an exam, and room temperature: which type is each?*
11. **Qon guruhi — nominal. Imtihondagi oʻrin — ordinal, chunki birinchi oʻrin ikkinchidan oldin turadi, lekin ular orasidagi farq teng emas. Harorat esa uzluksiz.**
    *Blood type is nominal. Exam place is ordinal: first comes before second, but the gaps are not equal. Temperature is continuous.*
12. **Endi bizda olti yuzta maosh bor, yaʼni sonli, uzluksiz berilganlar. Lekin bu olti yuz kishi kimlar? Bu butun soha emas, uning bir qismi xolos. Keyingi boʻlimda shu haqida gaplashamiz.**
    *Now we have six hundred salaries: numerical, continuous data. But who are these six hundred people? Not the whole industry, only part of it. That is the next section.*

### 2-boʻlim · Section 2 — Bosh toʻplam va tanlanma · Population and sample
1. **Bizda olti yuzta xodimning maoshi bor. Lekin odatda bizni kattaroq savol qiziqtiradi: butun sohada odamlar qancha maosh oladi?**
   *We have the salaries of six hundred employees. But the question we usually care about is bigger: what do people earn across the whole industry?*
   ▸ the 600 dots, then the camera pulls back: they sit inside a huge faint cloud
2. **Sohadagi hamma xodimni oʻlchab chiqolmaymiz, chunki ular juda koʻp. Biz oʻrganmoqchi boʻlgan hamma birliklar bosh toʻplam deb ataladi.**
   *We cannot measure every employee in the industry; there are far too many. Every unit we care about is called the population.*
3. **Haqiqatda oʻlchagan qismimiz esa tanlanma deyiladi. Mana bizning olti yuzta maoshimiz — bu tanlanma.**
   *The part we actually measure is the sample. Our six hundred salaries are a sample.*
   ▸ labels "bosh toʻplam (population)" around the cloud, "tanlanma (sample)" around the 600
3a. **Tanlanma foydali boʻlishi uchun u bosh toʻplamga oʻxshashi kerak. Agar maoshlarni faqat poytaxtdagi katta kompaniyalardan yigʻsak, butun soha haqidagi xulosamiz yuqori chiqadi. Shuning uchun tanlanmani tasodifiy olishga harakat qilamiz.**
   *A sample is only useful if it looks like the population. If we collected salaries only from big companies in the capital, our conclusion about the whole industry would come out too high. That is why we try to draw the sample at random.*
   ▸ the 600 dots drawn from one corner of the cloud (a red warning), then scattered evenly across it
4. **Keling, kichikroq misol olaylik. Beshta maosh, ming dollarda: oʻttiz bir, qirq besh, qirq yetti, ellik ikki va sakson sakkiz.**
   *Let's take a smaller example: five salaries, in thousands of dollars. Thirty-one, forty-five, forty-seven, fifty-two, and eighty-eight.*
   ▸ five cards
5. **Har birini nomlab olish uchun raqam beramiz: eks bir, eks ikki, va shunday qilib eks beshgacha. Nechta kuzatuv borligini en bilan belgilaymiz. Mana bu yerda en beshga teng.**
   *To name them, we number each one: x one, x two, and so on up to x five. We write the sample size as n; here n is five.*
   ▸ x₁ … x₅ appear under the cards, then "n = 5"
6. **Demak, eks uch — bu uchinchi kuzatuv, yaʼni qirq yetti. Eks besh esa sakson sakkiz.**
   *So x three is the third observation, forty-seven. And x five is eighty-eight.*
7. **Hammasini qoʻshish kerak boʻlsa, uzun qilib yozib oʻtirmaymiz. Sigma belgisi bilan yozamiz: ay birdan en gacha, eks ay larni qoʻshamiz.**
   *When we need to add them all up, we do not write it out longhand. We use the sigma sign: the sum of x i, for i from one to n.*
   ▸ x₁ + x₂ + x₃ + x₄ + x₅ folds into Σ xᵢ
8. **Mana bu yerda yigʻindi ikki yuz oltmish uchga teng.**
   *Here that comes to two hundred and sixty-three.*
9. **Yana bitta kelishuv bor. Tanlanmadan hisoblagan sonlarimizni lotin harflari bilan yozamiz: eks chiziqcha va es. Koʻrolmaydigan bosh toʻplamni esa grek harflari bilan yozamiz: myu va sigma.**
   *One more convention. Numbers computed from the sample get Latin letters: x bar and s. The population we cannot see gets Greek letters: mu and sigma.*
   ▸ two columns under the cloud and the sample: x̄, s │ μ, σ
9a. **Boshqacha aytganda: eks chiziqcha — biz hisoblay oladigan son, myu esa biz bilmoqchi boʻlgan son. Statistikaning butun ishi — birinchisidan ikkinchisi haqida xulosa chiqarish.**
   *Put another way: x bar is the number we can compute, and mu is the number we want to know. The whole job of statistics is to reason from the first to the second.*
   ▸ an arrow from x̄ (sample) to μ (cloud), labelled with a question mark
10. **Sunʼiy intellektda oʻqitish toʻplami — bu tanlanma. Model esa butun dunyoda, yaʼni bosh toʻplamda ishlashi kerak. Kursimiz davomida bu farqni koʻp marta uchratamiz.**
    *In AI, the training set is a sample. The model has to work on the whole world: the population. That gap comes back again and again in this course.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beshta maoshimizda eks ikki nechaga teng? Eks bir qoʻshuv eks besh-chi?**
    *Let's try it ourselves. Pause the video. In our five salaries, what is x two, and what is x one plus x five?*
12. **Eks ikki — qirq besh. Eks bir qoʻshuv eks besh — oʻttiz bir qoʻshuv sakson sakkiz, yaʼni bir yuz oʻn toʻqqiz.**
    *x two is forty-five. x one plus x five is thirty-one plus eighty-eight: one hundred and nineteen.*
13. **Xoʻp, olti yuzta maoshimiz bor. Lekin olti yuzta sonni bir qarashda qanday koʻramiz? Buni keyingi boʻlimda koʻramiz.**
    *So we have six hundred salaries. But how do we see the shape of six hundred numbers at a glance? That is the next section.*

### 3-boʻlim · Section 3 — Gistogramma · The histogram
1. **Olti yuzta maoshni roʻyxat qilib yozsak, hech narsani koʻrolmaymiz. Keling, ularni rasm qilib chizaylik.**
   *Written as a list, six hundred salaries show us nothing. Let's draw their shape instead.*
   ▸ the salary list scrolls, then collapses into dots on an axis
2. **Maosh uzluksiz kattalik, shuning uchun bir xil qiymat deyarli takrorlanmaydi. Har bir qiymatni alohida sanasak, hammasi bir martadan chiqadi.**
   *Salary is continuous, so almost no value repeats. If we count each value separately, every one of them appears exactly once.*
   ▸ 600 hair-thin bars, all the same height: 1
3. **Shuning uchun avval qiymatlarni sinflarga ajratamiz. Birinchi qadam — oraliqni topamiz. Eng kattasi bir yuz ellik bir ming, eng kichigi yigirma yetti ming. Oraliq bir yuz yigirma toʻrt ming dollar boʻladi.**
   *So first we group the values into classes. Step one is the range: the largest is one hundred and fifty-one thousand, the smallest twenty-seven thousand. The range is one hundred and twenty-four thousand dollars.*
   ▸ min and max dots light up, a brace between them: $124,026
4. **Ikkinchi qadam — nechta sinf boʻlishini tanlaymiz. Odatda beshtadan oʻntagacha olinadi. Biz yettita olamiz.**
   *Step two: choose the number of classes, usually five to ten. We take seven.*
5. **Uchinchi qadam — sinf kengligi. Oraliqni yettiga boʻlamiz, taxminan oʻn yetti ming yetti yuz chiqadi. Qulay boʻlishi uchun yigirma minggacha yaxlitlaymiz.**
   *Step three: the width. The range divided by seven is about seventeen thousand seven hundred. We round it up to a convenient twenty thousand dollars.*
   ▸ 124,026 ÷ 7 = 17,718 → 20,000; seven class edges drop onto the axis
5a. **Sinflar sonini tanlash muhim. Juda kam sinf olsak, masalan ikkita, hamma narsa ikkita ustunga qoʻshilib ketadi va shakl yoʻqoladi. Juda koʻp olsak, ustunlar siyrak va tishli boʻlib qoladi. Yaxshi gistogramma shu ikkisining oʻrtasida.**
   *The number of classes matters. Take too few, say two, and everything merges into two bars and the shape disappears. Take too many, and the bars become sparse and jagged. A good histogram sits between the two.*
   ▸ the same 600 salaries as 2 bars, then as 60 thin jagged bars, then back to 7
6. **Toʻrtinchi qadam — har bir sinfga nechta odam tushganini sanaymiz.**
   *Step four: count how many people fall into each class.*
   ▸ dots fall into the seven classes; counts tick up: 156, 311, 89, 32, 7, 3, 2
7. **Qirq mingdan oltmish minggacha uch yuz oʻn bir kishi bor, yaʼni yarmidan koʻpi. Undan yuqorida esa ingichka dum choʻzilib ketgan.**
   *Forty to sixty thousand: three hundred and eleven people, more than half. Above that, a thin tail stretches out to the right.*
8. **Beshinchi qadam — har bir sinfga bitta ustun chizamiz, ustunlar bir-biriga tegib turadi. Chunki shkala uzluksiz. Orada boʻshliq qoldirsak, goʻyo u yerda maosh boʻlishi mumkin emasdek koʻrinadi.**
   *Step five: draw one bar per class, with the bars touching. The scale is continuous; a gap would suggest salaries that cannot exist.*
   ▸ the stacks become touching bars; a gap flashes red, then closes
9. **Mana bu gistogramma deb ataladi. Bitta son koʻrsatolmaydigan narsani u koʻrsatadi: maoshlar oʻng tomonga qiyshaygan.**
   *This is a histogram. It shows what no single number can: the salaries are skewed to the right.*
9a. **Gistogramma shaklini shunday oʻqiymiz. Choʻqqisi oʻrtada va ikki tomoni bir xil boʻlsa — simmetrik. Dumi oʻngga choʻzilgan boʻlsa — oʻngga qiyshiq, maoshlar va uy narxlari kabi. Ikkita choʻqqi boʻlsa, berilganlarda ikki xil guruh aralashgan boʻlishi mumkin.**
   *We read a histogram's shape like this. Peak in the middle and both sides alike: symmetric. A tail stretching right: right-skewed, like salaries and house prices. Two peaks: the data may mix two different groups.*
   ▸ three small sketch histograms (labelled as illustrations): symmetric, right-skewed, two peaks
10. **Sunʼiy intellektda ham yangi berilganlar kelsa, birinchi ish shu: har bir belgining gistogrammasini chizamiz. Qanday taqsimlangan, qayerda gʻalati qiymatlar bor — shuni koʻramiz.**
    *In AI, the first thing we do with a new dataset is the same: draw a histogram of every feature, to see how it is spread and where the strange values are.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Jadvalga qarab, sakson mingdan koʻp oladiganlar nechta ekanini topamiz.**
    *Let's try it ourselves. Pause the video. Using the table, we find how many employees earn more than eighty thousand.*
12. **Oxirgi toʻrtta sinfni qoʻshamiz: oʻttiz ikki, yetti, uch va ikki. Jami qirq toʻrt kishi.**
    *We add the last four classes: thirty-two, seven, three and two. Forty-four people in all.*
13. **Lekin rahbarimiz baribir bitta son soʻraydi. Qaysi son? Buni keyingi boʻlimda koʻramiz.**
    *But our manager still asks for one number. Which one? That is the next section.*

### 4-boʻlim · Section 4 — Oʻrtacha qiymat · The mean  *(already built as its own video; folded into the lecture: greeting removed, Uzbek rewritten, "you" → "we", one new AI line; its Next card becomes the section 5 card)*
- s1a **Bu kompaniyada olti yuz kishi ishlaydi. Mana, har biri qancha maosh oladi. Rahbarimiz oddiy savol beradi: bu yerda odamlar qancha maosh oladi?** · *Six hundred people work at this company. Here is what every one of them earns. Our manager asks a simple question: what do people earn here?*
- s1b **Olti yuzta sonni bittalab oʻqib chiqolmaymiz. Hammasining oʻrnini bosadigan bitta son kerak. Lekin qaysi son?** · *We cannot read out six hundred numbers. We need one number that stands for all of them. But which one?*
- s2a **Eng oddiy javob — hammasini qoʻshamiz va teng qilib boʻlib chiqamiz.** · *The simplest answer: we add everything up and share it out equally.*
- s2b **Mana bu yerda ellik bir ming olti yuz oʻn uch dollar chiqdi. Buni oʻrtacha qiymat deymiz.** · *Here that comes to fifty-one thousand, six hundred and thirteen dollars. We call it the mean.*
- s2d **Formula bilan yozsak: eks ay larni qoʻshib, en ga boʻlamiz. Ikkinchi boʻlimdagi sigma belgisi aynan shu yerda kerak boʻldi.** · *As a formula: we add up the x i and divide by n. The sigma sign from section two is exactly what we need here.* ▸ x̄ = (1/n) Σ xᵢ
- s2c **Keling, u aslida nima qilayotganini koʻraylik. Kompaniyadagi hamma pulni yigʻib, teng boʻlib chiqsak, har bir kishiga mana shuncha tegadi.** · *Let's look at what it is really doing. It is the amount each person would get if all the money in the company were collected, and split evenly.*
- s3a **Shuning uchun umumiy summa muhim boʻlganda bizga aynan oʻrtacha qiymat kerak.** · *That is why the mean is what we want whenever totals matter.*
- s3e **Oʻrtachaga yana bir tomondan qaraylik. Har bir maoshni chiziq ustiga qoʻyilgan yuk deb tasavvur qilsak, oʻrtacha qiymat — chiziq muvozanatda turadigan nuqta. Markazdan uzoqdagi yuk koʻproq bosadi, shuning uchun bitta katta maosh oʻrtachani oʻziga tortadi.** · *Let's look at the mean from another side. If every salary were a weight placed on a beam, the mean is the point where the beam balances. A weight far from the centre presses harder, which is why one big salary pulls the mean towards itself.* ▸ the dot histogram on a beam over a triangle that slides to the balance point
- s3b **Uni olti yuzga koʻpaytirsak, butun ish haqi fondini qaytarib olamiz: oʻttiz bir millionga yaqin dollar.** · *Multiply it back by six hundred, and we recover the entire payroll: just under thirty-one million dollars.*
- s3c **Boshqa hech bir koʻrsatkich buni qilolmaydi. Oʻrtacha qiymat umumiy summani eslab qoladi.** · *No other summary does that. The mean is the one that remembers the total.*
- **s3d (new, AI)** **Sunʼiy intellektda ham shunday. Modelning xatosini butun berilganlar boʻyicha oʻrtacha qilamiz, oʻqitish esa aynan shu sonni kichraytiradi.** · *AI works the same way: we average a model's error over the whole dataset, and training is exactly the job of shrinking that average.* ▸ loss = (1/n) Σ errorᵢ
- s4a **Xoʻp, endi u qayerda adashishini koʻraylik. Oʻsha olti yuz xodimdan ellik nafari kafega boradi.** · *Now let's watch it fail. Fifty of those six hundred employees go out for a drink.*
- s4b **Ularning oʻrtacha maoshi ellik ming olti yuz yigirma yetti dollar. Oʻrtadagi odam esa qirq yetti ming uch yuz yigirma uch dollar oladi. Kutganimizdek, ikkalasi bir-biriga yaqin.** · *Their average salary is fifty thousand, six hundred and twenty-seven dollars, and the middle person earns forty-seven thousand, three hundred and twenty-three. Close together, as we would expect.*
- s4c **Keyin xonaga yana bir kishi kirib keladi — milliarder. Xonadagilarning hech biri bir tiyin ham boyib qolmadi.** · *Then one more person walks in: a billionaire. Nobody already in that room gained a single cent.*
- s4d **Lekin endi xonadagi oʻrtacha maosh ikki butun oʻndan toʻqqiz milliard dollar boʻldi.** · *But the average salary in that room is now two point nine billion dollars.*
- s4e **Keling, qizil chiziq qayerga tushganiga qaraylik. Boʻsh joyga, odamlar bilan milliarderning oʻrtasiga. Xonadagi hech kim bunday maosh olmaydi.** · *Let's look at where that red line lands. In empty space, between the crowd and the billionaire. It describes nobody present.*
- s5a **Endi uzuq chiziqqa qaraylik. Avval: qirq yetti ming uch yuz yigirma uch dollar.** · *Now let's look at the dashed line. Before: forty-seven thousand, three hundred and twenty-three.*
- s5b **Keyin: qirq yetti ming yetti yuz oltmish bir dollar. Bor-yoʻgʻi toʻrt yuz dollarga siljidi.** · *After: forty-seven thousand, seven hundred and sixty-one. It moved by four hundred dollars.*
- s5c **Mana shu chiziq mediana deb ataladi. U keyingi boʻlimimizning mavzusi.** · *That line is the median, and it is the subject of the next section.*
- s6a **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Mana toʻqqizta maosh, ming dollarda. Oʻrtacha qiymatini hisoblaymiz. Keyin toʻqqiz kishidan nechtasi undan kam olishini sanaymiz.** · *Let's try it ourselves. Pause the video. Here are nine salaries, in thousands of dollars. We work out the mean. Then we count how many of the nine earn less than it.*
- s6b **Yigʻindi toʻrt yuz ellik uch, demak oʻrtacha qiymat ellik ming uch yuz oʻttiz uch dollar.** · *The total is four hundred and fifty-three, so the mean is fifty thousand, three hundred and thirty-three dollars.*
- s6c **Toʻqqiz kishidan oltitasi undan kam oladi. Hech qanday milliarder yoʻq boʻlsa ham, oʻrtacha qiymat koʻpchilikdan yuqorida turibdi.** · *And six of the nine earn less than that. Even with no billionaire anywhere, the mean already sits above most of the people in it.*
- s7 **Mana shu muammoni mediana hal qiladi.** · *Which is exactly the problem the median solves.*

### 5-boʻlim · Section 5 — Mediana va mod · The median and the mode
1. **Avvalgi boʻlimda bitta milliarder oʻrtacha qiymatni boʻsh joyga olib ketdi. Keling, bunday paytda ham joyidan qimirlamaydigan son topaylik.**
   *In the last section, one billionaire dragged the mean into empty space. Let's find a number that holds its ground.*
2. **Gʻoya oddiy. Maoshlarni kichigidan kattasigacha tartib bilan teramiz va oʻrtada turgan odamni olamiz. Bu mediana deb ataladi.**
   *The idea is simple: we line the salaries up from smallest to largest, and take the person standing in the middle. That is the median.*
2a. **Oʻrtadagi oʻrinni topish oson: en qoʻshuv birni ikkiga boʻlamiz. Besh kishida bu uchinchi oʻrin, toʻqqiz kishida — beshinchi.**
   *Finding the middle position is easy: n plus one, divided by two. With five people that is the third place; with nine, the fifth.*
   ▸ (n + 1) / 2: 5 → 3, 9 → 5
3. **Beshta maosh: oʻttiz bir, qirq besh, qirq yetti, ellik ikki, sakson sakkiz. Ular tartiblangan, en beshga teng. Demak, oʻrtadagisi uchinchisi, yaʼni qirq yetti.**
   *Five salaries: thirty-one, forty-five, forty-seven, fifty-two, eighty-eight. They are sorted, n is five, so the middle one is the third: forty-seven.*
   ▸ five bars in a row; two from each end fade, the third glows
4. **Agar en juft boʻlsa-chi? Sakson sakkizni olib tashlaymiz. Toʻrtta qoldi, endi oʻrtada bitta emas, ikkita odam turibdi.**
   *What if n is even? Let's drop the eighty-eight. Now four are left, and there is not one middle person but two.*
5. **Bunday holatda ikkalasining oʻrtachasini olamiz. Qirq besh bilan qirq yetti — mediana qirq olti boʻladi.**
   *Then we take the average of those two: forty-five and forty-seven, so the median is forty-six.*
6. **Endi beshtasiga qaytaylik. Ularning oʻrtacha qiymati ellik ikki butun oʻndan olti. Bu beshta maoshdan toʻrttasidan katta! Bitta sakson sakkiz uni yuqoriga tortib ketdi. Mediana esa oʻrtadagi odamda qoldi.**
   *Back to the five. Their mean is fifty-two point six. That is larger than four of the five salaries! A single eighty-eight pulled it up, while the median stayed on the middle person.*
   ▸ red mean line at 52.6 above four bars; green median line on the third
7. **Demak, mediana odatiy odamni koʻrsatadi. Oʻrtacha qiymat esa umumiy summani teng boʻlsak, har kimga qancha tegishini koʻrsatadi.**
   *So the median describes a typical member of the sample. The mean describes each person's share if the total were split equally.*
7a. **Ikkalasini solishtirish ham foydali. Olti yuzta maoshimizda oʻrtacha qiymat ellik bir ming olti yuz dollar atrofida, mediana esa qirq yetti ming yetti yuz atrofida. Oʻrtacha medianadan yuqori — bu dum oʻngga choʻzilganining belgisi, gistogrammada koʻrganimizdek.**
   *Comparing the two is useful too. For our six hundred salaries the mean is about fifty-one thousand six hundred dollars, and the median about forty-seven thousand seven hundred. The mean above the median is the sign of a tail stretching right, just as the histogram showed.*
   ▸ the histogram of section 3 with both lines: mean (red) right of median (green)
8. **Shuning uchun statistika idoralari oilalar daromadini mediana bilan eʼlon qiladi. Uy narxlari ham xuddi shunday. Bir nechta milliarder yoki hashamatli uy oʻrtachani buzib yuboradi.**
   *That is why national statistics offices report median household income, and house prices the same way. A handful of billionaires or mansions would make the mean meaningless.*
9. **Yana bitta markaz bor — mod. Bu eng koʻp uchraydigan qiymat. Kategorial berilganlar uchun faqat mod ishlaydi: masalan, eng koʻp uchraydigan qon guruhi yoki doʻkonda eng koʻp sotiladigan oyoq kiyim oʻlchami.**
   *There is one more center: the mode, the value that appears most often. It is the only one that works for categorical data: the most common blood type, or the shoe size a shop sells most.*
10. **Demak, qoidamiz shunday. Simmetrik berilganlar va umumiy summa uchun — oʻrtacha qiymat. Qiyshiq berilganlar va juda katta qiymatlar boʻlsa — mediana. Kategorial berilganlar uchun — mod.**
    *Our rule of thumb: for symmetric data and for totals, the mean. For skewed data and extreme values, the median. For categorical data, the mode.*
    ▸ three cards, each with its data type icon
11. **Sunʼiy intellektda ham shunday. Berilganlardagi bitta xato, masalan bitta ortiqcha nol bilan yozilgan maosh, oʻrtachani buzib yuboradi, medianani esa deyarli qimirlatmaydi. Shuning uchun berilganlarni tozalashda koʻpincha medianaga tayanamiz.**
    *The same in AI: one error in the data, say a salary typed with an extra zero, wrecks the mean and barely moves the median. That is why data cleaning often leans on the median.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Avvalgi boʻlimdagi toʻqqizta maoshning medianasini topamiz.**
    *Let's try it ourselves. Pause the video. We find the median of the nine salaries from the last section.*
13. **Toʻqqizta qiymat bor, demak oʻrtadagisi beshinchisi — qirq yetti ming dollar. Oʻrtacha qiymat esa ellik ming uch yuz oʻttiz uch dollar edi.**
    *Nine values, so the middle one is the fifth: forty-seven thousand dollars. The mean was fifty thousand, three hundred and thirty-three.*
14. **Lekin markaz hamma narsani aytib bermaydi. Ikki xil berilganlarning oʻrtachasi bir xil boʻlib, oʻzi butunlay boshqacha boʻlishi mumkin. Buni keyingi boʻlimda koʻramiz.**
    *But a center does not tell the whole story. Two datasets can share the same mean and behave completely differently. That is the next section.*

### 6-boʻlim · Section 6 — Dispersiya · Variance
1. **Tasavvur qilamiz, ishga ikki xil yoʻl bilan borishimiz mumkin: avtobusda yoki mashinada. Besh kun avtobusda, besh kun mashinada yuramiz va vaqtini yozib boramiz.**
   *Let's imagine we can get to work two ways: by bus or by car. We time five days by bus and five days by car.*
2. **Avtobusda: oʻttiz, yigirma toʻqqiz, oʻttiz bir, oʻttiz, oʻttiz daqiqa. Mashinada: oʻn sakkiz, qirq ikki, yigirma besh, oʻttiz besh, oʻttiz daqiqa.**
   *Bus: thirty, twenty-nine, thirty-one, thirty, thirty minutes. Car: eighteen, forty-two, twenty-five, thirty-five, thirty minutes.*
   ▸ two rows of dots on a minutes axis
3. **Ikkalasining oʻrtachasi ham roppa-rosa oʻttiz daqiqa. Faqat oʻrtachaga qarasak, ular bir xil.**
   *Both average exactly thirty minutes. If we only look at the mean, they are the same.*
4. **Lekin mashinada bir kuni oʻn ikki daqiqa kechikdik. Demak, bizga qiymatlar qanchalik tarqoq ekanini oʻlchaydigan son kerak.**
   *But one day by car we were twelve minutes late. We need a number that measures spread.*
5. **Keling, har bir kun oʻrtachadan qancha farq qilishini topaylik. Mashinada: minus oʻn ikki, plyus oʻn ikki, minus besh, plyus besh va nol.**
   *Let's take each day's distance from the mean. By car: minus twelve, plus twelve, minus five, plus five, zero.*
   ▸ arrows from the mean line to each car dot
6. **Shunchaki qoʻshsak, nol chiqadi, chunki musbatlar bilan manfiylar bir-birini yeb qoʻyadi. Shuning uchun har birini kvadratga oshiramiz.**
   *If we simply add them, we get zero: the pluses and minuses cancel. So we square each one first.*
   ▸ each arrow grows into a square: 144, 144, 25, 25, 0
6a. **Ishorani yoʻqotishning boshqa yoʻli ham bor — modulni olish. Lekin kvadrat katta farqlarni ogʻirroq hisoblaydi: oʻn ikki daqiqalik farq besh daqiqalikdan bor-yoʻgʻi ikki baravardan sal koʻp, uning kvadrati esa besh baravardan ham koʻp.**
   *There is another way to drop the sign: take the absolute value. But squaring weighs big distances more heavily: a twelve-minute distance is just over twice a five-minute one, while its square is more than five times as large.*
   ▸ 12 vs 5 as bars, then 144 vs 25 as squares
7. **Kvadratlarni qoʻshsak, uch yuz oʻttiz sakkiz chiqadi. Uni en minus birga, yaʼni toʻrtga boʻlamiz: sakson toʻrt butun oʻndan besh. Mana shu dispersiya deb ataladi.**
   *The squares add up to three hundred and thirty-eight. We divide by n minus one, that is four: eighty-four point five. This is the variance.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Avtobusning dispersiyasini ham xuddi shunday hisoblaymiz.**
   *Let's try it ourselves. Pause the video. We work out the bus's variance the same way.*
9. **Avtobusda farqlar bor-yoʻgʻi minus bir va plyus bir. Kvadratlar yigʻindisi ikki, dispersiya esa nol butun oʻndan besh.**
   *By bus the distances are only minus one and plus one. The squares add up to two, so the variance is zero point five.*
10. **Dispersiyaning birligi daqiqaning kvadrati, bu biroz gʻalati. Shuning uchun ildizdan chiqaramiz va standart chetlanishni olamiz: mashinada taxminan toʻqqiz daqiqa, avtobusda bir daqiqaga ham yetmaydi.**
    *Variance is measured in squared minutes, which is an odd unit. Taking the square root gives the standard deviation: about nine minutes by car, less than one minute by bus.*
10a. **Standart chetlanishni shunday tushunamiz: bir kunlik yoʻl oʻrtachadan odatda qancha uzoqlashadi. Mashinada toʻqqiz daqiqacha, avtobusda bir daqiqadan kam. Bitta son ishonchlilikni aytib beradi.**
    *Here is how to read the standard deviation: how far a typical day's trip strays from the mean. About nine minutes by car, under a minute by bus. One number tells us how reliable each one is.*
    ▸ a band of ±s around the mean line on each row of dots
11. **Nima uchun en ga emas, en minus birga boʻlamiz? Chunki oʻrtachani shu tanlanmaning oʻzidan hisobladik. Shuning uchun u tanlanmaga haqiqiy oʻrtachadan doim biroz yaqinroq boʻladi. En minus birga boʻlib, shu kamchilikni tuzatamiz.**
    *Why n minus one, not n? We computed the mean from the sample itself, so it always sits a little closer to the sample than the true mean does. Dividing by n minus one corrects for that.*
12. **Sunʼiy intellektda ikki modelning oʻrtacha aniqligi bir xil boʻlsa, natijasi har safar sakrab turadiganini emas, barqarorini tanlaymiz. Bu farqni aynan dispersiya koʻrsatadi.**
    *In AI, between two models with the same average accuracy, we choose the steady one over the one that jumps around from run to run. Variance is what shows the difference.*
13. **Keyingi boʻlimda dispersiya qanday qilib haqiqiy pulga va chiqindiga aylanishini koʻramiz.**
    *In the next section, we see how variance turns into real money and real waste.*

### 7-boʻlim · Section 7 — Tarqoqlik — bu xavf · Variance is risk
1. **Keling, ichimlik zavodiga boraylik. Shishaga besh yuz millilitr deb yozilgan. Qonun boʻyicha toʻrt yuz toʻqson beshdan besh yuz beshgacha boʻlishi mumkin.**
   *Let's visit a bottling plant. The label says five hundred millilitres, and the law allows four hundred and ninety-five to five hundred and five.*
   ▸ a fill axis with the 495–505 band shaded
2. **Zavodda ikkita mashina bor. Ikkalasi ham oʻrtacha roppa-rosa besh yuz millilitr quyadi.**
   *There are two machines, and both fill exactly five hundred millilitres on average.*
3. **Birinchi mashinaning standart chetlanishi ikki millilitr. Chegaralar oʻrtachadan ikki yarim standart chetlanish uzoqda turibdi. Shuning uchun mingta shishadan bor-yoʻgʻi oʻn bittasi yaroqsiz chiqadi.**
   *Machine A has a standard deviation of two millilitres. The limits sit two and a half standard deviations out, so only eleven bottles in a thousand are rejected.*
   ▸ a narrow bell inside the band; a grid of 1000 bottles, 11 turn red
3a. **Ikki yarim standart chetlanish nimani anglatadi? Chegaragacha besh millilitr, standart chetlanish esa ikki. Beshni ikkiga boʻlsak, ikki yarim chiqadi. Yaʼni shisha chegaradan chiqishi uchun odatdagidan ikki yarim baravar koʻp adashishi kerak, bu esa kamdan-kam boʻladi.**
   *What do two and a half standard deviations mean? The limit is five millilitres away, and the standard deviation is two. Five divided by two is two and a half. So a bottle must miss by two and a half times the usual amount to fall outside, and that is rare.*
   ▸ 5 ÷ 2 = 2.5, the distance to the limit marked off in standard deviations
4. **Ikkinchi mashinaning standart chetlanishi toʻrt millilitr. Endi oʻsha chegaralar bor-yoʻgʻi bir butun toʻrtdan bir standart chetlanish uzoqda. Mingtadan ikki yuz oʻntasi yaroqsiz, yaʼni har beshinchi shisha.**
   *Machine B has a standard deviation of four millilitres. Now the same limits are only one and a quarter standard deviations out. Two hundred and ten in a thousand are rejected: one bottle in five.*
   ▸ a wide bell spilling past the band; 210 of the 1000 turn red
4a. **Ikkinchi mashinada beshni toʻrtga boʻlamiz: bir butun toʻrtdan bir. Chegaradan chiqish uchun odatdagi adashishdan sal koʻprogʻi yetarli.**
   *For machine B, five divided by four: one and a quarter. Missing by only a little more than usual is enough to fall outside.*
   ▸ 5 ÷ 4 = 1.25
5. **Tarqoqlik ikki baravar oshdi, chiqindi esa oʻn toʻqqiz baravar koʻpaydi. Oʻrtacha qiymat esa bir millilitr ham oʻzgarmadi.**
   *The spread doubled, and the waste went up nineteen times. The mean never moved by a single millilitre.*
6. **Demak, zavod faqat oʻrtachani emas, tarqoqlikni ham nazorat qilishi kerak. Sifat nazoratidagi mashhur «Olti Sigma» gʻoyasi aynan shu.**
   *So the plant has to control the spread, not just the average. That is the whole idea behind Six Sigma quality control.*
7. **Kundalik hayotda ham shunday: vaqtida keladigan avtobus, navbati oldindan maʼlum boʻlgan klinika, haroratni bir xil ushlab turadigan pech. Oʻrtacha qiymat ishlar qanchalik tez-tez buzilishini hech qachon aytmaydi.**
   *Everyday life is the same: a bus that keeps its timetable, a clinic with predictable waiting times, an oven that holds its temperature. The average never tells us how often things go wrong.*
8. **Sunʼiy intellektda ham modelning bashoratidan tashqari, uning qanchalik ishonchsizligini, yaʼni tarqoqligini baholaymiz. Shunda modelga qachon ishonmaslik kerakligini bilamiz.**
   *In AI, we estimate not just a model's prediction but its uncertainty, its spread, so we know when not to trust it.*
9. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Ikkinchi mashinaning tarqoqligini kamaytirolmasak, uning oʻrtachasini qayerga qoʻyishimiz kerak?**
   *Let's think it through. Pause the video. If we cannot reduce machine B's spread, where should we set its average?*
10. **Aynan chegaralarning oʻrtasiga. Oʻrtachani qaysi tomonga sursak ham, bitta chegara yaqinlashadi va yaroqsiz shishalar koʻpayadi.**
    *Right in the middle of the limits. Whichever way we move the average, one limit gets closer, and more bottles are rejected.*
11. **Lekin dispersiya bitta juda katta qiymatga ham sezgir. Shunday qiymatlardan buzilmaydigan tarqoqlik oʻlchovi bormi? Buni keyingi boʻlimda koʻramiz.**
    *But variance is very sensitive to a single extreme value. Is there a measure of spread that survives outliers? That is the next section.*

### 8-boʻlim · Section 8 — Kvartillar va quti diagrammasi · Quartiles and box plots
1. **Mediana markazni juda katta qiymatlardan himoya qildi. Keling, tarqoqlik uchun ham xuddi shunday himoya quraylik.**
   *The median protected the center from outliers. Let's build the same protection for spread.*
2. **Toʻqqizta maoshimizni tartib bilan teramiz. Mediana beshinchisi, yaʼni qirq yetti. U berilganlarni ikki yarmiga ajratadi.**
   *We take our nine salaries, sorted. The median is the fifth, forty-seven. It splits the data into two halves.*
   ▸ nine bars; the fifth glows and a divider drops
3. **Pastki yarmi: oʻttiz bir, oʻttiz sakkiz, qirq ikki, qirq besh. Uning medianasi oʻttiz sakkiz bilan qirq ikkining oʻrtachasi, yaʼni qirq. Bu birinchi kvartil deb ataladi, kyu bir.**
   *The lower half: thirty-one, thirty-eight, forty-two, forty-five. Its median is the average of thirty-eight and forty-two: forty. That is the first quartile, Q one.*
4. **Yuqori yarmi: qirq toʻqqiz, ellik ikki, oltmish bir, sakson sakkiz. Uning medianasi ellik olti yarim. Bu uchinchi kvartil, kyu uch.**
   *The upper half: forty-nine, fifty-two, sixty-one, eighty-eight. Its median is fifty-six and a half. That is the third quartile, Q three.*
4a. **Kvartillarni boshqacha ham tushunish mumkin: berilganlarning choragi kyu birdan past, yarmi medianadan past, toʻrtdan uch qismi kyu uchdan past. «Kvartil» soʻzining oʻzi ham chorak degani.**
   *Quartiles can be read another way too: a quarter of the data lies below Q one, half below the median, three quarters below Q three. The word quartile itself means quarter.*
   ▸ the nine bars split into four groups by Q1, median, Q3
5. **Endi beshta son bilan berilganlarni tasvirlaymiz: eng kichigi, kyu bir, mediana, kyu uch va eng kattasi. Oʻttiz bir, qirq, qirq yetti, ellik olti yarim va sakson sakkiz.**
   *Now five numbers describe the data: the minimum, Q one, the median, Q three and the maximum. Thirty-one, forty, forty-seven, fifty-six and a half, eighty-eight.*
6. **Kyu uchdan kyu birni ayirsak, kvartillararo oraliq chiqadi, qisqacha ay kyu ar. Bu oʻrtadagi yarim berilganlarning kengligi. Mana bu yerda oʻn olti yarim. U ham medianaga oʻxshab, juda katta qiymatlardan buzilmaydi.**
   *Q three minus Q one is the interquartile range, the IQR: the width of the middle half of the data. Here, sixteen and a half. Like the median, it survives extreme values.*
6a. **Nega u buzilmaydi? Sakson sakkizni sakson sakkiz million qilsak ham, kyu uch oʻzgarmaydi: u qiymatga emas, tartibdagi oʻringa qarab olinadi.**
   *Why does it survive? Even if we turned eighty-eight into eighty-eight million, Q three would not change: it is taken by position in the order, not by value.*
   ▸ the last bar shoots off the top; Q3 and the IQR stay put
7. **Endi chetga chiqqan qiymatlarni topamiz. Kyu uchga bir yarim ay kyu ar qoʻshamiz: sakson bir butun yuzdan yigirma besh chiqadi. Bundan yuqoridagi har qanday qiymat chetga chiqqan hisoblanadi.**
   *Now we can flag outliers. Add one and a half IQRs to Q three: eighty-one point two five. Anything above that counts as an outlier.*
8. **Sakson sakkiz bu chegaradan oshib ketdi. Demak, sakson sakkiz ming dollarlik maosh — chetga chiqqan qiymat.**
   *Eighty-eight is past that fence. So the eighty-eight thousand dollar salary is flagged as an outlier.*
9. **Endi hammasini bitta rasmga chizamiz: kyu birdan kyu uchgacha quti, ichida mediana chizigʻi, ikki tomonda moʻylovlar va alohida nuqta — chetga chiqqan qiymat. Bu quti diagrammasi deb ataladi.**
   *We draw all of this as one picture: a box from Q one to Q three, a median line inside, whiskers, and a separate dot for the outlier. This is a box plot.*
   ▸ the nine bars turn sideways and collapse into the box plot
10. **Uning kuchi guruhlarni solishtirganda koʻrinadi. Xizmat koʻrsatish markazining uchta filialida kutish vaqtini olaylik. Ey filialida mediana oʻn bir butun oʻndan sakkiz daqiqa, bi filialida oʻn yetti butun oʻndan yetti, si filialida esa yigirma toʻqqiz yarim.**
    *Its strength is comparing groups. Waiting times at three branches of a service centre: branch A has a median of eleven point eight minutes, branch B seventeen point seven, branch C twenty-nine point five.*
    ▸ three box plots side by side
11. **Si filiali ham eng sekin, ham eng beqaror: uning qutisi deyarli yigirma daqiqa keng. Bitta oʻrtacha son qaysi filialni tuzatish kerakligini koʻrsatib berolmas edi.**
    *Branch C is both the slowest and the most variable: its box is almost twenty minutes wide. A single average would not tell us which branch to fix.*
12. **Sunʼiy intellektda modelni oʻqitishdan oldin aynan shu qoida bilan gʻalati qiymatlarni topamiz: xato yozilgan yozuvlar, sensor xatolari va hokazo.**
    *In AI, before training a model we use exactly this rule to catch strange values: mistyped records, sensor glitches.*
13. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Pastki chegarani hisoblaymiz, yaʼni kyu birdan bir yarim ay kyu ar ni ayiramiz. Undan pastda qiymat bormi?**
    *Let's try it ourselves. Pause the video. We work out the lower fence, Q one minus one and a half IQRs. Is any value below it?*
14. **Pastki chegara oʻn besh butun yuzdan yigirma besh. Eng kichik maosh oʻttiz bir. Demak, pastda chetga chiqqan qiymat yoʻq.**
    *The lower fence is fifteen point two five. The smallest salary is thirty-one, so there is no outlier at the bottom.*
15. **Lekin beshta son ham bizni aldashi mumkin. Keyingi boʻlimda statistikasi bir xil, lekin rasmi butunlay boshqacha boʻlgan toʻrtta berilganlar toʻplamini koʻramiz.**
    *But even five numbers can fool us. In the next section, four datasets with the same statistics and completely different pictures.*

### 9-boʻlim · Section 9 — Berilganlarni doim chizamiz · Always plot the data (Anscombe)
1. **Keling, toʻrtta berilganlar toʻplamini olaylik. Har birida oʻn bittadan nuqta bor.**
   *Let's take four datasets. Each has eleven points.*
   ▸ four tables of numbers, no plots yet
2. **Ularning statistikasini hisoblaymiz. Eks ning oʻrtachasi toʻrttasida ham toʻqqiz. Uay ning oʻrtachasi ham toʻrttasida yetti yarim.**
   *Let's compute their statistics. The mean of x is nine in all four. The mean of y is seven and a half in all four.*
3. **Eks ning dispersiyasi hammasida oʻn bir. Korrelyatsiya hammasida taxminan nol butun mingdan sakkiz yuz oʻn olti. Hatto eng yaxshi toʻgʻri chiziq ham bir xil: uay teng uch qoʻshuv eks ning yarmi.**
   *The variance of x is eleven in all of them. The correlation is about zero point eight one six in all of them. Even the best-fitting line is the same: y equals three plus half of x.*
3a. **Korrelyatsiya — ikki kattalik birgalikda toʻgʻri chiziq boʻylab qanchalik oʻzgarishini koʻrsatadigan son, u minus birdan birgacha boʻladi. Uni toʻqqizinchi maʼruzada batafsil oʻrganamiz. Hozircha shuni bilsak yetarli: nol butun sakkiz — kuchli bogʻlanishdek koʻrinadi.**
   *Correlation is a number from minus one to one that says how closely two quantities move together along a straight line. We study it in detail in Lecture 9. For now it is enough to know that zero point eight looks like a strong relationship.*
   ▸ a scale from −1 to 1 with 0.816 marked
4. **Raqamlarga qarasak, toʻrttasi ham bir xil. Xoʻp, endi ularni chizib koʻraylik.**
   *By the numbers, these are the same dataset four times. Now let's draw them.*
5. **Birinchisi — oddiy chiziqli bogʻlanish, atrofida biroz tarqoqlik bor. Mana bu yerda toʻgʻri chiziq toʻgʻri keladi.**
   *The first: an ordinary straight-line relationship with some scatter. Here, a line fits.*
6. **Ikkinchisi — mukammal egri chiziq. Bu yerda toʻgʻri chiziq umuman notoʻgʻri model.**
   *The second: a perfect curve. Here, a straight line is the wrong model entirely.*
7. **Uchinchisi — mukammal toʻgʻri chiziq, lekin bitta chetga chiqqan nuqta chiziqni oʻziga tortib ketgan.**
   *The third: a perfect line, but one outlier pulls the fitted slope toward itself.*
8. **Toʻrtinchisida esa hech qanday bogʻlanish yoʻq. Faqat bitta uzoqdagi nuqta kuchli korrelyatsiya bordek koʻrsatyapti.**
   *The fourth: no relationship at all. A single far-off point fakes a strong correlation.*
9. **Bu toʻrtta toʻplamni statistik Frensis Enskomb ming toʻqqiz yuz yetmish uchinchi yilda aynan shuni koʻrsatish uchun eʼlon qilgan: berilganlarni chizmasdan turib, statistikaga ishonmang.**
   *The statistician Francis Anscombe published these four datasets in nineteen seventy-three for exactly this reason: never trust the statistics without plotting the data.*
10. **Sunʼiy intellektda bu juda muhim. Aniqlik kabi bitta son model toʻgʻri tanlanganini aytmaydi. Modelga ishonishdan oldin uning nuqtalarini va xatolarini doim chizib koʻramiz.**
    *In AI this matters a lot: one number like accuracy does not tell us the model is the right one. Before we trust a model, we always plot its points and its errors.*
11. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Toʻrttasidan qaysi birida toʻgʻri chiziqli model haqiqatan toʻgʻri keladi?**
    *Let's think it through. Pause the video. In which of the four is a straight-line model actually right?*
12. **Faqat birinchisida. Qolgan uchtasida oʻsha chiziq bizni aldaydi.**
    *Only the first. In the other three, the same line misleads us.*
13. **Mana shu bilan nolinchi qismni tugatamiz. Keyingi qismda noaniqlikni oʻlchashni oʻrganamiz, yaʼni ehtimollikni.**
    *That brings part zero to an end. In the next part we learn to measure uncertainty: probability.*

---

## Part 1 — Ehtimollik
▸ part card "1-qism · Ehtimollik"

### 10-boʻlim · Section 10 — Namunalar fazosi, hodisa, ehtimollik · Sample space, event, probability
1. **Xoʻp, endi maʼruzamizning birinchi qismiga oʻtamiz. Ertaga yomgʻir yogʻadimi? Kubik olti koʻrsatadimi? Keling, bunday savollarni songa aylantirishni oʻrganaylik.**
   *Now we move on to part one of our lecture. Will it rain tomorrow? Will the die show a six? Let's learn to turn questions like these into numbers.*
2. **Birinchi qadam — natijaga qarashdan oldin, nima boʻlishi mumkin boʻlsa, hammasini yozib chiqamiz. Kubikda bu bir, ikki, uch, toʻrt, besh, olti. Buni namunalar fazosi deymiz va omega bilan belgilaymiz.**
   *Step one: before we look, we write down everything that could happen. For a die, that is one, two, three, four, five, six. We call this the sample space, and write it as omega.*
   ▸ six die faces drop into a set Ω
3. **Tangada: gerb yoki raqam. Ertangi kun uchun: yomgʻir yogʻadi yoki yogʻmaydi.**
   *For a coin: heads or tails. For tomorrow: rain or no rain.*
4. **Ikkinchi qadam — savolimizni yozamiz. Kubik juft son koʻrsatadimi? Javobi «ha» boʻladigan natijalarni yigʻamiz: ikki, toʻrt, olti. Mana shu toʻplam hodisa deb ataladi.**
   *Step two: we write down our question. Will the die show an even number? We collect the outcomes that answer yes: two, four, six. That set is called an event.*
   ▸ 2, 4, 6 lift out of Ω into a ring labelled A
5. **Uchinchi qadam — har bir hodisaga noldan birgacha bitta son beramiz. Nol — boʻlishi mumkin emas, bir — albatta boʻladi. Omeganing ehtimoli doim bir, chunki nimadir albatta sodir boʻladi.**
   *Step three: we give each event one number between zero and one. Zero means impossible, one means certain. The probability of omega is always one, because something must happen.*
6. **Toʻgʻri kubikda juft son chiqish ehtimoli: oltitadan uchtasi, yaʼni ikkidan bir.**
   *For a fair die, the probability of an even number is three outcomes out of six: one half.*
6a. **Ikkidan bir degani nima? Kubikni koʻp marta tashlasak, taxminan yarmida juft son chiqadi. Lekin bu juft va toq navbat bilan keladi degani emas: ketma-ket uch marta juft chiqishi ham odatiy, uning ehtimoli sakkizdan bir.**
   *What does one half mean? If we roll the die many times, an even number comes up about half the time. But that does not mean even and odd take turns: three evens in a row is ordinary, with probability one in eight.*
   ▸ a strip of rolls with a run of three evens highlighted
7. **Nima uchun toʻplamlar bilan ishlaymiz? Chunki savol toʻplamga aylansa, «yoki» birlashma boʻladi, «va» kesishma boʻladi, «emas» esa toʻldiruvchi boʻladi. Qolgan hisobni qoidalar qiladi.**
   *Why bother with sets? Because once a question is a set, "or" becomes a union, "and" becomes an intersection, and "not" becomes a complement. Then the rules do the counting for us.*
8. **Sunʼiy intellektda klassifikator aynan shunday ishlaydi. Har bir sinf uchun noldan birgacha ehtimol beradi va ularning yigʻindisi birga teng boʻladi.**
   *In AI, a classifier works exactly like this: it outputs a probability between zero and one for each class, and they add up to one.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Kubik toʻrtdan katta son koʻrsatadi» degan hodisani yozamiz va ehtimolini topamiz.**
   *Let's try it ourselves. Pause the video. We write down the event "the die shows more than four", and find its probability.*
10. **Besh va olti. Oltitadan ikkitasi, yaʼni uchdan bir.**
    *Five and six. Two out of six: one third.*
11. **Keyingi boʻlimda bu ehtimollarni birlashtiradigan uchta qoidani koʻramiz.**
    *In the next section, the three rules that combine these probabilities.*

### 11-boʻlim · Section 11 — Uchta qoida · The three rules
1. **Oddiy hodisalarning ehtimolini topishni bilamiz. Murakkab hodisalarnikini qanday topamiz? Buning uchun uchta qoida yetarli.**
   *We have the probabilities of simple events. How do we get them for complicated ones? Three rules are enough.*
2. **Birinchisi — toʻldiruvchi qoidasi. Ey sodir boʻlmasligining ehtimolini topish uchun birdan ey ning ehtimolini ayiramiz. Juft son chiqmasligi: birdan ikkidan birni ayiramiz, yaʼni ikkidan bir.**
   *The first is the complement rule. The probability that A does not happen is one minus the probability of A. Not even: one minus a half, which is a half.*
3. **Bu qoida «hech boʻlmaganda bittasi» degan savollarda juda qulay: hech biri boʻlmasligini hisoblab, birdan ayiramiz.**
   *It is the easy way into "at least one" questions: we work out "none", and subtract it from one.*
4. **Ikkinchisi — qoʻshish qoidasi. Keling, ellik ikkita kartadan bittasini olaylik. Yurak belgili karta chiqishi — ellik ikkidan oʻn uch. Qirol chiqishi — ellik ikkidan toʻrt.**
   *The second is the addition rule. Let's draw one card from fifty-two. A heart: thirteen out of fifty-two. A king: four out of fifty-two.*
   ▸ the 52-card grid; the hearts row and the kings column light up
5. **Yurak yoki qirol chiqish ehtimoli-chi? Oʻn uch qoʻshuv toʻrt emas. Chunki yurak qiroli ikkala guruhda ham bor, uni ikki marta sanab qoʻyamiz.**
   *What about a heart or a king? Not thirteen plus four. The king of hearts is in both groups; we would count it twice.*
   ▸ the crossing card flashes
5a. **Rasmda buni ikki doira deb koʻramiz: ikkalasining yuzini qoʻshsak, ustma-ust tushgan joy ikki marta sanaladi.**
   *In a picture these are two circles: add their areas and the overlap is counted twice.*
   ▸ two overlapping circles, the overlap flashing twice
6. **Shuning uchun kesishmani bir marta ayiramiz: oʻn uch qoʻshuv toʻrt minus bir, yaʼni ellik ikkidan oʻn olti.**
   *So we subtract the overlap once: thirteen plus four minus one, sixteen out of fifty-two.*
7. **Uchinchisi — koʻpaytirish qoidasi. Ey va bi ning birga sodir boʻlish ehtimolini topish uchun ey ning ehtimolini ey sodir boʻlgandagi bi ning ehtimoliga koʻpaytiramiz.**
   *The third is the multiplication rule. The probability of A and B together is the probability of A, times the probability of B given that A has happened.*
8. **Masalan, yurak qiroli. Avval yurak chiqishi — ellik ikkidan oʻn uch. Yurak chiqqanini bilsak, uning qirol boʻlishi — oʻn uchdan bir. Koʻpaytirsak, ellik ikkidan bir chiqadi.**
   *The king of hearts: first a heart, thirteen out of fifty-two. Given it is a heart, the chance it is a king is one in thirteen. Multiply them: one out of fifty-two.*
9. **Mana shu «… sodir boʻlgandagi» degan tushuncha shartli ehtimollik deb ataladi. Uni ikkinchi maʼruzada chuqur oʻrganamiz.**
   *That word "given" is conditional probability. We study it in depth in Lecture 2.*
9a. **Endi ikki qoidani birga ishlatamiz. Kubikni toʻrt marta tashlaymiz. Hech boʻlmaganda bitta olti chiqishi ehtimoli qancha? Bitta tashlashda olti chiqmasligi — oltidan besh. Toʻrt marta chiqmasligi — oltidan beshning toʻrtinchi darajasi, taxminan nol butun yuzdan qirq sakkiz. Demak, hech boʻlmaganda bitta olti — taxminan nol butun yuzdan ellik ikki.**
   *Now we use two rules together. We roll a die four times. What is the chance of at least one six? No six on one roll: five sixths. No six in four rolls: five sixths to the fourth power, about zero point four eight. So at least one six: about zero point five two.*
   ▸ (5/6)⁴ ≈ 0.48, 1 − 0.48 ≈ 0.52
10. **Sunʼiy intellektda til modeli gapni aynan koʻpaytirish qoidasi bilan baholaydi: har bir soʻzning ehtimolini oldingi soʻzlarga qarab hisoblaydi va hammasini koʻpaytiradi.**
    *In AI, a language model scores a sentence with exactly the multiplication rule: the probability of each word given the words before it, all multiplied together.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Karta yurak ham, qirol ham boʻlmaslik ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. What is the probability that the card is neither a heart nor a king?*
12. **Toʻldiruvchi qoidasi bilan: birdan ellik ikkidan oʻn oltini ayiramiz, yaʼni ellik ikkidan oʻttiz olti.**
    *The complement rule: one minus sixteen out of fifty-two, which is thirty-six out of fifty-two.*
13. **Keyingi boʻlimda toʻldiruvchi qoidasi deyarli hammani aldaydigan savolga javob beradi.**
    *In the next section, the complement rule answers a question that fools almost everyone.*

### 12-boʻlim · Section 12 — Tugʻilgan kun masalasi · The birthday problem
1. **Xonada nechta odam boʻlsa, ikkitasining tugʻilgan kuni bir xil boʻlish ehtimoli yarimdan oshadi? Koʻpchilik yuz saksonta atrofida deb oʻylaydi.**
   *How many people must be in a room before the chance that two share a birthday passes one half? Most people guess around one hundred and eighty.*
2. **Keling, toʻgʻridan-toʻgʻri sanab koʻraylik: kimdir kim bilandir bir kunda tugʻilgan hamma holatlarni. Juftlar, uchliklar, bir nechta juftlar — sanash tezda chalkashib ketadi.**
   *Let's try to count it directly: every case where someone shares a birthday with someone. Pairs, triples, several pairs at once; the counting gets messy fast.*
2a. **Avvalgi boʻlimdagi toʻldiruvchi qoidasini eslaymiz: «hech boʻlmaganda bitta» oʻrniga «hech biri»ni hisoblash osonroq.**
   *Recall the complement rule from the last section: instead of "at least one", it is easier to compute "none".*
3. **Shuning uchun teskarisini hisoblaymiz: hammaning tugʻilgan kuni har xil boʻlsin. Keyin buni birdan ayiramiz.**
   *So we compute the opposite: everyone's birthday is different. Then we subtract it from one.*
4. **Birinchi odam istalgan kunda tugʻilishi mumkin. Ikkinchisi qolgan uch yuz oltmish toʻrt kunning birida tugʻilishi kerak. Uchinchisi uch yuz oltmish uch kunning birida, va hokazo.**
   *The first person can have any birthday. The second must land on one of the other three hundred and sixty-four days. The third on one of three hundred and sixty-three, and so on.*
   ▸ a 365-cell calendar; each new person takes a free cell
5. **Shu kasrlarni koʻpaytiramiz va natijani birdan ayiramiz.**
   *We multiply those fractions together, and subtract the result from one.*
5a. **Yigirma uch kishi uchun bu koʻpaytma shunday: uch yuz oltmish beshdan uch yuz oltmish besh, karra uch yuz oltmish beshdan uch yuz oltmish toʻrt, va shunday davom etib, uch yuz oltmish beshdan uch yuz qirq uchgacha.**
   *For twenty-three people the product reads: three sixty-five over three sixty-five, times three sixty-four over three sixty-five, and so on down to three forty-three over three sixty-five.*
   ▸ 365/365 · 364/365 · … · 343/365
6. **Oʻn kishi boʻlsa, ehtimol bor-yoʻgʻi oʻn ikki foiz. Yigirma uch kishi boʻlsa, ellik butun oʻndan yetti foiz. Yarimdan oshdi!**
   *With ten people the chance is only twelve percent. With twenty-three, it is fifty point seven percent. Past one half!*
   ▸ the curve draws itself point by point; a marker stops at 23
7. **Ellik kishida toʻqson yetti foiz, yetmish kishida esa deyarli aniq.**
   *With fifty people, ninety-seven percent. With seventy, almost certain.*
8. **Nima uchun sezgimiz adashadi? Chunki biz oʻzimizni boshqalar bilan solishtiramiz. Aslida esa har bir juftlik hisobga kiradi: yigirma uch kishidan ikki yuz ellik uchta juftlik chiqadi.**
   *Why does our intuition fail? Because we compare ourselves with the others. In fact every pair counts: twenty-three people make two hundred and fifty-three pairs.*
   ▸ 23 dots, then all 253 connecting lines
9. **Kompyuter fanlari va sunʼiy intellektda xuddi shu hisob bilan xesh toʻqnashuvlari va berilganlardagi takrorlanishlar baholanadi: ular biz kutganimizdan ancha tez paydo boʻladi.**
   *In computing and AI, the same calculation estimates hash collisions and duplicates in data: they show up much sooner than we expect.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻttiz kishilik guruhda ehtimol qancha? Grafikdan topamiz.**
    *Let's try it ourselves. Pause the video. In a class of thirty, what is the chance? Let's read it off the curve.*
11. **Taxminan yetmish bir foiz. Demak, oʻttiz kishilik guruhlarning koʻpchiligida tugʻilgan kuni bir xil boʻlgan juftlik bor.**
    *About seventy-one percent. Most classes of thirty have a shared birthday.*
12. **Bu hisobda biz odamlarning tugʻilgan kunlari bir-biriga bogʻliq emas deb oldik. «Bogʻliq emas» degani aslida nima? Buni keyingi boʻlimda koʻramiz.**
    *In that calculation we assumed people's birthdays have nothing to do with each other. What does that really mean? That is the next section.*

### 13-boʻlim · Section 13 — Istisno qiluvchi va erkli hodisalar · Mutually exclusive vs. independent
1. **Ikkita tushuncha koʻpincha adashtiriladi: bir-birini istisno qiluvchi hodisalar va erkli hodisalar. Keling, farqini kubik misolida koʻraylik.**
   *Two ideas get mixed up all the time: mutually exclusive and independent. Let's see the difference on a die.*
2. **Ikki hodisa hech qachon birga sodir boʻlmasa, ular bir-birini istisno qiladi. Kesishmasi boʻsh, birga sodir boʻlish ehtimoli nol.**
   *Two events are mutually exclusive if they can never happen together: their overlap is empty, and the probability of both is zero.*
3. **Ikki hodisaning birga sodir boʻlish ehtimoli ularning ehtimollari koʻpaytmasiga teng boʻlsa, ular erkli deyiladi. Yaʼni birini bilish ikkinchisi haqida hech narsa aytmaydi.**
   *Two events are independent if the probability of both equals the product of their probabilities. In other words, knowing one tells us nothing about the other.*
3a. **Hayotiy misol: tanga va kubikni birga tashlaymiz. Tangada gerb chiqqani kubikka hech qanday taʼsir qilmaydi. Shuning uchun ular erkli.**
   *An everyday example: we toss a coin and roll a die together. The coin landing heads does nothing to the die. That is why they are independent.*
   ▸ a coin and a die side by side, no arrow between them
4. **Kubik tashlaymiz. Ey — juft son: ikki, toʻrt, olti, ehtimoli ikkidan bir. Bi — toʻrtdan katta son: besh, olti, ehtimoli uchdan bir.**
   *We roll a die. A is "even": two, four, six, with probability one half. B is "more than four": five, six, with probability one third.*
   ▸ Venn diagram over the six faces
5. **Ikkalasi birga faqat oltida boʻladi, ehtimoli oltidan bir. Ikkidan birni uchdan birga koʻpaytirsak ham oltidan bir chiqadi. Demak, ey va bi erkli.**
   *Both together: only six, with probability one sixth. And one half times one third is also one sixth. So A and B are independent.*
6. **Lekin ular bir-birini istisno qilmaydi, chunki olti ikkalasida ham bor.**
   *But they are not mutually exclusive: six belongs to both.*
7. **Xoʻp, endi teskarisini olaylik: juft va toq. Ular bir-birini istisno qiladi. Ular erklimi?**
   *Now the reverse: even and odd. They are mutually exclusive. Are they independent?*
8. **Yoʻq! Son juft chiqqanini bilsak, toq emasligini aniq bilamiz. Bu kuchli bogʻliqlik. Ehtimollar koʻpaytmasi toʻrtdan bir, haqiqiy ehtimol esa nol.**
   *No! If we know the number came up even, we know for certain it is not odd. That is strong dependence. The product of the probabilities is one quarter, but the real probability is zero.*
9. **Demak, qoida shunday: ehtimoli noldan katta boʻlgan ikkita istisno qiluvchi hodisa doim bogʻliq boʻladi.**
   *The rule: two mutually exclusive events with nonzero probability are always dependent.*
9a. **Farqni eslab qolish uchun: istisno qilish — rasm haqida, doiralar kesishmaydi. Erklilik esa sonlar haqida, uni rasmdan koʻrib boʻlmaydi, koʻpaytirib tekshiramiz.**
   *To remember the difference: mutual exclusion is about the picture, the circles do not overlap. Independence is about the numbers: we cannot see it in the picture, we check it by multiplying.*
   ▸ two panels: non-overlapping circles │ P(A ∩ B) = P(A) · P(B)
10. **Sunʼiy intellektda mashhur sodda Bayes klassifikatori aynan erklilik farazi ustiga qurilgan: u har bir soʻzni boshqa soʻzlardan erkli deb hisoblaydi.**
    *In AI, the well-known naive Bayes classifier is built on exactly this assumption: it treats each word as independent of the others.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Juft son» va «uchdan kichik son» hodisalari erklimi?**
    *Let's try it ourselves. Pause the video. Are the events "even" and "less than three" independent?*
12. **Kesishmasi faqat ikki, ehtimoli oltidan bir. Ikkidan birni uchdan birga koʻpaytirsak ham oltidan bir. Demak, erkli.**
    *Their overlap is only two: one sixth. One half times one third is also one sixth. So they are independent.*
13. **Hozirgacha biz toʻgʻri kubikda sanadik. Lekin hayotda hamma natijalar teng ehtimolli boʻlishi kamdan-kam uchraydi. Buni keyingi boʻlimda koʻramiz.**
    *So far we have counted on a fair die. But in the real world, equally likely outcomes are rare. That is the next section.*

### 14-boʻlim · Section 14 — Klassik va empirik ehtimollik · Classical vs. empirical probability
1. **Ob-havo maʼlumotida eshitamiz: ertaga yomgʻir yogʻish ehtimoli yetmish foiz. Bu son qayerdan olinadi?**
   *The weather forecast says: seventy percent chance of rain tomorrow. Where does that number come from?*
2. **Kubikda biz klassik ehtimollikdan foydalandik. Hamma natijalar teng ehtimolli boʻlsa, hodisadagi natijalar sonini jami natijalar soniga boʻlamiz.**
   *On the die, we used classical probability: when all outcomes are equally likely, we divide the outcomes in the event by the total number of outcomes.*
3. **Ob-havoda esa teng ehtimolli natijalar yoʻq, sanaydigan fazomiz ham yoʻq.**
   *Weather has no equally likely outcomes. There is no sample space to count.*
4. **Buning oʻrniga oʻtmishga qaraymiz: bugungidek sharoit boʻlgan oʻtgan kunlarning taxminan yetmish foizida yomgʻir yoqqan. Bu empirik ehtimollik deb ataladi.**
   *Instead, we look at the past: of all past days with conditions like today's, it rained on about seventy percent. That is empirical probability.*
   ▸ a grid of past days filling with rain/no-rain icons (labelled as an illustration)
5. **Formulasi oddiy: hodisa necha marta kuzatilganini jami kuzatuvlar soniga boʻlamiz.**
   *The formula is simple: the number of times the event was observed, divided by the total number of observations.*
5a. **Kuzatuvlar qancha koʻp boʻlsa, empirik ehtimollik shuncha barqaror boʻladi. Oʻnta kunga qarab «yetmish foiz» deyish xavfli, oʻn mingta kunga qarab esa unga ishonsa boʻladi. Nega shunday ekanini beshinchi maʼruzada koʻramiz.**
   *The more observations, the steadier the empirical probability. Saying "seventy percent" from ten days is risky; from ten thousand days we can trust it. Lecture 5 shows why.*
   ▸ the share of rainy days plotted against the number of days, wobbling then settling (labelled as an illustration)
6. **Masalan, olti yuzta xodimimizdan uch yuz oʻn bittasi qirq mingdan oltmish minggacha oladi. Demak, tasodifiy tanlangan xodimning shu oraliqda boʻlish ehtimoli taxminan ellik ikki foiz.**
   *For example, of our six hundred employees, three hundred and eleven earn between forty and sixty thousand. The empirical probability that a random employee lands there is about fifty-two percent.*
   ▸ the histogram from section 3; the 40–60k bar lifts out: 311 / 600
7. **Sunʼiy intellekt deyarli doim empirik ehtimollikka tayanadi: oʻqitish toʻplamidagi sinflar ulushi, matnlardagi soʻzlar chastotasi, reklamani bosishlar ulushi va hokazo.**
   *AI almost always relies on empirical probability: class shares in a training set, word frequencies in a corpus, click-through rates in logs.*
8. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Spam filtrni toʻqson foizi spam boʻlgan berilganlarda oʻqitdik. Shu berilganlardan olingan spam ehtimoli haqiqiy pochtaga toʻgʻri keladimi?**
   *Let's think it through. Pause the video. We trained a spam filter on data where ninety percent of emails are spam. Is the spam probability from that data right for real email?*
9. **Yoʻq. Empirik ehtimollik faqat berilganlar olingan joy uchun toʻgʻri. Tanlanma bosh toʻplamga oʻxshamasa, ehtimol ham notoʻgʻri chiqadi.**
   *No. An empirical probability is only right for the place the data came from. If the sample does not look like the population, the probability is wrong too.*
10. **Keling, maʼruzani yakunlaylik. Berilganlar turi qaysi hisob toʻgʻri ekanini belgilaydi. Oʻrtacha qiymat umumiy summani eslab qoladi, mediana esa juda katta qiymatlardan buzilmaydi. Dispersiya va ay kyu ar xavfni oʻlchaydi. Berilganlarni doim chizib koʻramiz. Ehtimollik qoidalari esa murakkab hodisalarni oddiylari orqali hisoblaydi.**
    *Let's wrap up the lecture. The type of data decides which calculations are valid. The mean remembers the total; the median survives outliers. Variance and the IQR measure risk. We always plot the data. And the probability rules build complex events from simple ones.*
11. **Mana shu bilan birinchi maʼruzamizni tugatamiz. Keyingi maʼruzada «… sodir boʻlgandagi» degan soʻzning kuchini koʻramiz: shartli ehtimollik va Bayes teoremasi.**
    *That brings our first lecture to an end. In the next lecture, we see the power of the word "given": conditional probability and Bayes' theorem.*
