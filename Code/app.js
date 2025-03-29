async function search() {
    try {
        const cityInput = document.getElementById('realCity').value.trim().toLowerCase();
        const stateInput = document.getElementById('realState').value.trim().toLowerCase();
        const firstInput = document.getElementById('realFirst').value.trim().toLowerCase();
        const lastInput = document.getElementById('realLast').value.trim().toLowerCase();
        const dateInput = document.getElementById('realAge').value.trim().toLowerCase();

        const exactMatchCheckbox = document.getElementById('exactMatch');
        const isExactMatch = exactMatchCheckbox ? exactMatchCheckbox.checked : false;

        const response = await fetch('kids.csv');
        if (!response.ok) throw new Error(`Failed to fetch CSV: ${response.status}`);

        const text = await response.text();
        const rows = text.split('\n').map(line => line.split(',').map(cell => (cell || '').replace(/^"|"$/g, '').trim().toLowerCase()));
        const header = rows.shift();

        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';

        let found = false;
        let count = 0;

        for (let row of rows) {
            if (row.length < 8) continue;

            const riskScore = row[0];
            const city = row[1];
            const state = row[2];
            const age = row[3];
            const dateMissing = row[4];
            const firstName = row[5];
            const lastName = row[6];
            const cluster = row[7];

            const showAll = cityInput === '' && stateInput === '' && firstInput === '' && lastInput === '' && dateInput === '';

            let isMatch = showAll || (
                (!isExactMatch && (
                    (cityInput === '' || city.includes(cityInput)) &&
                    (stateInput === '' || state.includes(stateInput)) &&
                    (firstInput === '' || firstName.includes(firstInput)) &&
                    (lastInput === '' || lastName.includes(lastInput)) &&
                    (dateInput === '' || dateMissing.includes(dateInput))
                )) || 
                (isExactMatch && (
                    (cityInput === '' || city === cityInput) &&
                    (stateInput === '' || state === stateInput) &&
                    (firstInput === '' || firstName === firstInput) &&
                    (lastInput === '' || lastName === lastInput) &&
                    (dateInput === '' || dateMissing === dateInput)
                ))
            );

            if (isMatch) {
                found = true;
                count++;

                resultsDiv.innerHTML += `
                <div class="bg-white shadow rounded-xl p-4 mb-4 transition hover:scale-105 mx-auto w-full max-w-xl">
                    <h2 class="font-bold text-lg mb-2">${capitalize(firstName)} ${capitalize(lastName)}</h2>
                    <p><strong>Location:</strong> ${capitalize(city)}, ${state.toUpperCase()}</p>
                    <p><strong>Age:</strong> ${age}</p>
                    <p><strong>Date Missing:</strong> ${dateMissing}</p>
                    <p><strong>Risk Score:</strong> ${riskScore} | <strong>Cluster:</strong> ${cluster}</p>
                </div>`;
            }
        }

        if (!found) {
            resultsDiv.innerHTML = `
            <div class="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-xl shadow mx-auto text-center w-fit max-w-lg mt-4">
                <strong class="font-bold text-lg block">No Results Found</strong>
                <p class="text-sm mt-2">Try adjusting your search or double-checking your inputs.</p>
            </div>`;
        } else {
            resultsDiv.innerHTML = `<p class="mb-4 text-gray-600 text-center">${count} result${count !== 1 ? 's' : ''} found</p>` + resultsDiv.innerHTML;
        }
    } catch (error) {
        console.error("Error during search:", error);
        document.getElementById('results').innerHTML = `<p class="text-red-500 text-center">An error occurred while searching: ${error.message}</p>`;
    }
}

function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}
