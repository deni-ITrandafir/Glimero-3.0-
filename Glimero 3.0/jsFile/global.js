document.addEventListener("DOMContentLoaded", function () {
    const input = document.querySelector("input[name='name']");
    const suggestionBox = document.createElement("div");
    suggestionBox.classList.add("autocomplete-suggestions");
    document.body.appendChild(suggestionBox);

    input.addEventListener("input", function () {
        const query = input.value.trim();

        // ascunde sugestiile daca inputul e gol sau nu sunt mai multe de 3 caractere introduse 
        if (query.length < 3) {
            suggestionBox.style.display = "none";
            return;
        }

        fetch(`/autocomplete?q=${query}`)
            .then(response => response.json())
            .then(suggestions => {
                suggestionBox.innerHTML = "";
                if (suggestions.length > 0) {
                    suggestions.forEach(suggestion => {
                        const item = document.createElement("div");
                        item.textContent = suggestion;
                        item.classList.add("suggestion-item");

                        item.addEventListener("click", function () {
                            input.value = suggestion;
                            suggestionBox.style.display = "none";
                        });

                        suggestionBox.appendChild(item);
                    });

                    const rect = input.getBoundingClientRect();
                    suggestionBox.style.left = `${rect.left}px`;
                    suggestionBox.style.top = `${rect.bottom + window.scrollY}px`;
                    suggestionBox.style.width = `${rect.width}px`;
                    suggestionBox.style.display = "block";
                } else {
                    suggestionBox.style.display = "none";
                }
            })
            .catch(err => console.error("Autocomplete error:", err));
    });

    // cand utilizatorul face click in alta parte se ascund sugestiile
    document.addEventListener("click", function (e) {
        if (!suggestionBox.contains(e.target) && e.target !== input) {
            suggestionBox.style.display = "none";
        }
    });
});