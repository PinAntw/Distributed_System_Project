document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const checkinForm = document.getElementById("checkinForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const response = await fetch("/auth/login", {
                method: "POST",
                body: JSON.stringify(Object.fromEntries(formData)),
                headers: { "Content-Type": "application/json" }
            });
            alert(await response.text());
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            await fetch("/auth/register", {
                method: "POST",
                body: JSON.stringify(Object.fromEntries(formData)),
                headers: { "Content-Type": "application/json" }
            });
            alert("註冊成功!");
            window.location.href = "/";
        });
    }

    if (checkinForm) {
        checkinForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(checkinForm);
            await fetch("/post/checkin", {
                method: "POST",
                body: JSON.stringify(Object.fromEntries(formData)),
                headers: { "Content-Type": "application/json" }
            });
            alert("打卡成功!");
        });
    }

    // 排名數據
    if (document.getElementById("rankingTable")) {
        fetch("/ranking/top20")
            .then(res => res.json())
            .then(data => {
                const table = document.getElementById("rankingTable");
                table.innerHTML = data.map((team, index) =>
                    `<tr>
                        <td>${index + 1}</td>
                        <td>${team.name}</td>
                        <td>${team.score}</td>
                    </tr>`
                ).join("");
            });
    }
});
