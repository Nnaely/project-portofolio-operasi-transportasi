(() => {
  'use strict';
  const d = window.ANALYSIS_DATA;
  const $ = id => document.getElementById(id);
  const nf = new Intl.NumberFormat('en-US');
  const n = x => nf.format(x);
  const money = x => '$' + Number(x).toFixed(2);
  const routes = ['JFK → Manhattan','LaGuardia → Manhattan','Manhattan → Manhattan'];
  const classes = ['jfk','lga','city'];
  const colors = ['#995d13','#376b70','#737a82'];
  const periodName = {full:'January–April 2025',train:'January–March 2025',holdout:'April 2025'};
  if (location.protocol === 'file:') {
    document.querySelectorAll('a[href="downloads/analysis-project.zip"]').forEach(a=>{a.href='../../README.md';a.removeAttribute('download');a.textContent='Open project README ↗';});
  }
  if (!d || !Array.isArray(d.groups)) { $('finding').textContent = 'Results could not be loaded. Open the executive memo for the verified findings.'; return; }
  function aggregate(rows) {
    const trips=rows.reduce((s,r)=>s+r.trips,0),fare=rows.reduce((s,r)=>s+r.fare_usd,0),minutes=rows.reduce((s,r)=>s+r.occupied_minutes,0);
    return {trips,fare_usd:fare,occupied_minutes:minutes,mean_fare_usd:fare/trips,mean_minutes:minutes/trips,fare_per_occupied_hour:fare/minutes*60};
  }
  function selectedGroups(period) { return routes.map(route=>({route,...aggregate(d.groups.filter(x=>x.route===route&&(period==='full'||x.period===period)))})); }
  const full = selectedGroups('full');
  const studyCount = full.reduce((s,r)=>s+r.trips,0);
  $('source-count').textContent=n(d.kpis.source_trips);
  $('eligible-count').textContent=n(d.kpis.eligible_trips);
  $('route-count').textContent=n(studyCount);
  const best=[...full].sort((a,b)=>b.fare_per_occupied_hour-a.fare_per_occupied_hour)[0];
  const city=full[2];
  $('finding').textContent=`${best.route.split(' → ')[0]} has the highest base fare per occupied hour (${money(best.fare_per_occupied_hour)} versus ${money(city.fare_per_occupied_hour)} within Manhattan). Unrecorded waiting and repositioning time can change that comparison.`;
  $('quality-note').textContent=`${n(d.kpis.source_trips-d.kpis.eligible_trips)} source records fall outside the primary cohort. Trips touching the March 9 daylight-saving transition date are also excluded because the supplied timestamps have no UTC offset. The downloadable project records each exclusion separately.`;
  function bars(id,groups,field) {
    const max=Math.max(...groups.map(g=>g[field]))*1.05;
    $(id).innerHTML=groups.map((g,i)=>`<div class="route-bar ${classes[i]}"><header><span>${g.route}</span><strong>${money(g[field])}</strong></header><div class="track" role="img" aria-label="${g.route}: ${money(g[field])}"><div class="fill" style="width:${g[field]/max*100}%"></div></div></div>`).join('');
  }
  function scenario() {
    const period=$('period').value,groups=selectedGroups(period),cityExtra=Number($('city-wait').value),airportExtra=Number($('airport-wait').value);
    $('city-wait-value').textContent=cityExtra+' min';$('airport-wait-value').textContent=airportExtra+' min';
    const rates=groups.map((g,i)=>g.fare_usd/(g.occupied_minutes+g.trips*(i===2?cityExtra:airportExtra))*60);
    $('cycle-results').innerHTML=groups.map((g,i)=>`<div class="cycle-item"><span>${g.route}</span><strong>${money(rates[i])}<small> / h</small></strong></div>`).join('');
    const cityRate=rates[2];
    $('break-even').textContent=groups.slice(0,2).map(g=>{const wait=60*g.mean_fare_usd/cityRate-g.mean_minutes;return wait<0?`${g.route.split(' → ')[0]} is below the city benchmark even with zero extra minutes.`:`${g.route.split(' → ')[0]}: ${wait.toFixed(1)} extra minutes per trip.`}).join(' ');
  }
  function hourly() {
    const period=$('period').value;
    const series=routes.map(route=>Array.from({length:24},(_,hour)=>({hour,...aggregate(d.hourly.filter(r=>r.route===route&&r.hour===hour&&(period==='full'||r.period===period)))})));
    const valid=series.flat().filter(r=>r.trips>=100);
    const W=960,H=300,L=50,R=25,T=25,B=40,pw=W-L-R,ph=H-T-B;
    const max=Math.ceil(Math.max(...valid.map(r=>r.fare_per_occupied_hour))/20)*20;
    const x=h=>L+h/23*pw,y=v=>T+ph-v/max*ph;
    const grid=Array.from({length:5},(_,i)=>{const v=i*max/4;return `<line x1="${L}" x2="${W-R}" y1="${y(v)}" y2="${y(v)}" stroke="#d5d8cf"/><text x="${L-10}" y="${y(v)+4}" text-anchor="end">$${v.toFixed(0)}</text>`}).join('');
    const ticks=Array.from({length:24},(_,h)=>h%3===0||h===23?`<text x="${x(h)}" y="${H-12}" text-anchor="middle">${String(h).padStart(2,'0')}:00</text>`:'').join('');
    const lines=series.map((rows,i)=>{let connected=false;const path=rows.map(r=>{if(r.trips<100){connected=false;return '';}const value=`${connected?'L':'M'} ${x(r.hour)} ${y(r.fare_per_occupied_hour)}`;connected=true;return value;}).join(' ');const dots=rows.filter(r=>r.trips>=100).map(r=>`<circle cx="${x(r.hour)}" cy="${y(r.fare_per_occupied_hour)}" r="3.2" fill="${colors[i]}" tabindex="0" aria-label="${routes[i]}, ${r.hour}:00, ${money(r.fare_per_occupied_hour)} per occupied hour, ${n(r.trips)} trips"><title>${routes[i]} · ${r.hour}:00 · ${money(r.fare_per_occupied_hour)}/h · ${n(r.trips)} trips</title></circle>`).join('');return `<path d="${path}" fill="none" stroke="${colors[i]}" stroke-width="2.2" ${i===2?'stroke-dasharray="6 4"':''}/>${dots}`}).join('');
    $('hourly-chart').innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Base fare per occupied hour by pickup hour for three routes"><title>${periodName[period]}: pickup-hour fare productivity</title>${grid}${ticks}${lines}</svg>`;
  }
  function compare() {
    const period=$('period').value,groups=selectedGroups(period);
    $('scope-note').textContent=`${periodName[period]} · ${n(groups.reduce((s,r)=>s+r.trips,0))} trips across the three routes. This selector updates the comparison, time scenario, and hourly chart. The April validation below stays fixed.`;
    bars('fare-chart',groups,'mean_fare_usd');bars('productivity-chart',groups,'fare_per_occupied_hour');
    $('route-table').innerHTML=groups.map(g=>`<tr><td>${g.route}</td><td>${n(g.trips)}</td><td>${g.mean_minutes.toFixed(1)}</td><td>${money(g.mean_fare_usd)}</td><td>${money(g.fare_per_occupied_hour)}</td></tr>`).join('');
    scenario();hourly();
  }
  function holdout() {
    const h=d.holdout;
    $('train-winner').textContent=h.training_winner;$('holdout-winner').textContent=h.holdout_winner;
    const tr=d.groups.find(g=>g.route===h.training_winner&&g.period==='train'),ho=d.groups.find(g=>g.route===h.holdout_winner&&g.period==='holdout');
    $('train-detail').textContent=`${money(tr.fare_per_occupied_hour)} per occupied hour from ${n(tr.trips)} trips.`;
    $('holdout-detail').textContent=`${money(ho.fare_per_occupied_hour)} per occupied hour from ${n(ho.trips)} trips.`;
    $('holdout-verdict').textContent=h.ranking_preserved?'The route ordering persists in April. That supports the stability of this descriptive comparison. It does not establish a gain from changing dispatch.':'The route ordering changes in April. Treat the historical ranking as unstable; do not turn it into a dispatch rule.';
    if(d.bootstrap?.comparisons?.length){
      $('confidence-table').innerHTML='<table><thead><tr><th>Comparison with Manhattan</th><th>Window</th><th>Productivity ratio</th><th>95% day-bootstrap interval</th></tr></thead><tbody>'+d.bootstrap.comparisons.filter(r=>r.route!==routes[2]).map(r=>`<tr><td>${r.route}</td><td>${r.period==='train'?'Jan–Mar':'April'}</td><td>${r.ratio_to_city.toFixed(2)}×</td><td>${r.ratio_ci_low.toFixed(2)}–${r.ratio_ci_high.toFixed(2)}×</td></tr>`).join('')+'</tbody></table>';
      $('bootstrap-note').textContent=`Uncertainty uses ${n(d.bootstrap.replicates)} paired resamples of calendar days. It reflects variation within the observed period; seasonality, unobserved waiting time and vehicle-level dependence remain outside this interval.`;
    }
  }
  $('period').addEventListener('change',compare);$('city-wait').addEventListener('input',scenario);$('airport-wait').addEventListener('input',scenario);
  compare();holdout();
})();
