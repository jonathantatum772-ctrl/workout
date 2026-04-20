  <script>
    // ----- time matching logic -----
    const target = {minutes};
    const picks = document.querySelectorAll('.exercise-pick');
    const status = document.getElementById('time-status');

    function updateSelectedTime() {{
      if (!status) return;
      let total = 0;
      picks.forEach(p => {{
        if (p.checked) total += Number(p.dataset.mins || 0);
      }});
      if (total >= target) {{
        status.innerHTML = `<strong>Selected time:</strong> ${{total}} min ✅ target met`;
        status.className = 'ok';
      }} else {{
        status.innerHTML = `<strong>Selected time:</strong> ${{total}} min (need ${{target - total}} more)`;
        status.className = 'warn';
      }}
    }}

    picks.forEach(p => p.addEventListener('change', updateSelectedTime));
    updateSelectedTime();

    // ----- set tracking persistence -----
    const setBoxes = document.querySelectorAll('.set-box');
    setBoxes.forEach((box, idx) => {{
      const key = 'setbox-' + idx;
      box.checked = localStorage.getItem(key) === '1';
      box.addEventListener('change', () => {{
        localStorage.setItem(key, box.checked ? '1' : '0');
      }});
    }});

    // ----- rest timers -----
    const timers = {{}};

    function fmt(sec) {{
      const m = String(Math.floor(sec / 60)).padStart(2, '0');
      const s = String(sec % 60).padStart(2, '0');
      return `${{m}}:${{s}}`;
    }}

    window.startTimer = function(exId, duration) {{
      stopTimer(exId);
      let left = duration;
      const el = document.getElementById(`timer-${{exId}}`);
      if (!el) return;
      el.textContent = fmt(left);

      timers[exId] = setInterval(() => {{
        left -= 1;
        el.textContent = fmt(Math.max(left, 0));
        if (left <= 0) {{
          clearInterval(timers[exId]);
          el.textContent = "DONE ✅";
          try {{ new Audio("https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg").play(); }} catch (e) {{}}
        }}
      }}, 1000);
    }}

    window.stopTimer = function(exId) {{
      if (timers[exId]) {{
        clearInterval(timers[exId]);
        delete timers[exId];
      }}
      const el = document.getElementById(`timer-${{exId}}`);
      if (el) el.textContent = "00:00";
    }}
  </script>
