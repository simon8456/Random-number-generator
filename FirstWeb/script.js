// Najdi prvky pro tlačítko, výsledek, vstupy a historii
const button = document.getElementById("generateButton");
const result = document.getElementById("result");
const minValueInput = document.getElementById("minValue");
const maxValueInput = document.getElementById("maxValue");
const historyList = document.getElementById("history");
const clearHistoryButton = document.getElementById("clearHistoryButton");

// Přidej událost kliknutí na tlačítko generování
button.addEventListener("click", () => {
    const minValue = parseInt(minValueInput.value) || 1; // Defaultní hodnota: 1
    const maxValue = parseInt(maxValueInput.value) || 100; // Defaultní hodnota: 100

    // Ověř, zda jsou hodnoty validní
    if (minValue >= maxValue) {
        result.textContent = "Chyba: Minimální hodnota musí být menší než maximální.";
        result.style.color = "red";
        return;
    }

    // Simulace "počítání" před zobrazením finálního čísla
    result.textContent = "Generuji...";
    result.style.color = "black";

    setTimeout(() => {
        // Vygeneruj náhodné číslo v zadaném rozsahu
        const randomNumber = Math.floor(Math.random() * (maxValue - minValue + 1)) + minValue;

        // Zobraz číslo
        result.textContent = `Vygenerované číslo: ${randomNumber}`;

        // Přidej číslo do historie
        const listItem = document.createElement("li");
        listItem.textContent = randomNumber;
        historyList.appendChild(listItem);
    }, 1000); // Zpoždění 1 sekunda
});

// Přidej událost kliknutí na tlačítko pro vymazání historie
clearHistoryButton.addEventListener("click", () => {
    historyList.innerHTML = ""; // Vymaže celý seznam historie
});
