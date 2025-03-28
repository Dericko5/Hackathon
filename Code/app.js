async function search() {
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const first = document.getElementById('first').value;
    const last = document.getElementById('last').value;
    const date = document.getElementById('date').value;

    const url = `http://challenge.us-hpccsystems-dev.azure.lnrsg.io:8002/WsEcl/submit/query/MyQuerySet/FindMissingKid.json?in_city=${city}&in_state=${state}&in_first=${first}&in_last=${last}&in_dateMissing=${date}`;

    const res = await fetch(url);
    const data = await res.json();

    const resultDiv = document.getElementById('results');
    resultDiv.innerHTML = '';

    if (data && data.Results && data.Results.MissingKidResults && data.Results.MissingKidResults.Row) {
        data.Results.MissingKidResults.Row.forEach(kid => {
            resultDiv.innerHTML += `<div class='bg-white p-4 rounded-xl shadow-sm'>
                <p><strong>Name:</strong> ${kid.FirstName} ${kid.LastName}</p>
                <p><strong>City:</strong> ${kid.MissingCity}, <strong>State:</strong> ${kid.MissingState}</p>
                <p><strong>Age:</strong> ${kid.CurrentAge} | <strong>Date Missing:</strong> ${kid.DateMissing}</p>
            </div>`;
        });
    } else {
        resultDiv.innerHTML = '<p class="text-red-500">No results found.</p>';
    }
}