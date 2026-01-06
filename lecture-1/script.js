const areaSelect = document.getElementById("areaSelect");
const weatherDiv = document.getElementById("weather");

// 地域リスト取得
fetch("https://www.jma.go.jp/bosai/common/const/area.json")
  .then(res => res.json())
  .then(data => {
    const areas = data.offices;

    for (const code in areas) {
      const option = document.createElement("option");
      option.value = code;
      option.textContent = areas[code].name;
      areaSelect.appendChild(option);
    }
  });

// 地域選択時の天気取得
areaSelect.addEventListener("change", () => {
  const areaCode = areaSelect.value;
  if (!areaCode) return;

  fetch(`https://www.jma.go.jp/bosai/forecast/data/forecast/${areaCode}.json`)
    .then(res => res.json())
    .then(data => {
      const forecast = data[0].timeSeries[0].areas[0];
      weatherDiv.innerHTML = `
        <h2>${forecast.area.name}</h2>
        <p>今日の天気：${forecast.weathers[0]}</p>
      `;
    });
});
