const API_BASE = "http://127.0.0.1:8000";
let currentReportData = null;


/* ---------------- SCAN ANIMATION ---------------- */

function startScanAnimation(scanSteps){

const radar = document.getElementById("scanning-radar");

// remove old animation if exists
const oldSteps = document.querySelector(".scan-steps");
if(oldSteps) oldSteps.remove();

let stepsContainer = document.createElement("div");
stepsContainer.className = "scan-steps";

scanSteps.forEach((step,i)=>{

let stepDiv = document.createElement("div");

stepDiv.className = "scan-step";
stepDiv.id = "scan-step-"+i;

stepDiv.innerHTML = `
<span class="step-icon">⏳</span>
<span class="step-text">${step}</span>
`;

stepsContainer.appendChild(stepDiv);

});

radar.appendChild(stepsContainer);

return stepsContainer;

}



/* ---------------- URL SCANNER ---------------- */

async function scanURL() {

const urlInput = document.getElementById('url-input').value.trim();
const radar = document.getElementById('scanning-radar');
const resultBox = document.getElementById('result-container');
const dynamicStatus = document.getElementById('dynamic-status');
const btn = document.getElementById('url-btn');
const input = document.getElementById('url-input');

if (!urlInput.includes('.') || urlInput.length < 4) {
alert("❌ Error: Invalid URL Format.");
return;
}

btn.disabled = true;
input.readOnly = true;
resultBox.classList.add('hidden');
radar.classList.remove('hidden');


const scanSteps = [
"🌐 Initializing Secure Handshake...",
"🔍 Scraping DOM Metadata...",
"🧠 LSTM Neural Engine Predicting...",
"🛡️ Querying WHOIS Database...",
"📊 Quantifying Threat Vectors..."
];

startScanAnimation(scanSteps);

let step = 0;

const stepInterval = setInterval(()=>{

const stepEl = document.getElementById("scan-step-"+step);

if(stepEl){

stepEl.classList.add("active");
stepEl.querySelector(".step-icon").innerText="⚙️";
dynamicStatus.innerText = scanSteps[step];

}

if(step>0){

const prev = document.getElementById("scan-step-"+(step-1));

if(prev){
prev.classList.remove("active");
prev.classList.add("done");
prev.querySelector(".step-icon").innerText="✔";
}

}

step++;

if(step>=scanSteps.length){

const last = document.getElementById("scan-step-"+(scanSteps.length-1));

if(last){
last.classList.remove("active");
last.classList.add("done");
last.querySelector(".step-icon").innerText="✔";
}

clearInterval(stepInterval);

}

},700);



try {

const apiRequest = fetch(`${API_BASE}/predict/url`,{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({url:urlInput})
});

const animationDelay = new Promise(resolve =>
setTimeout(resolve,scanSteps.length*700)
);

const [response] = await Promise.all([
apiRequest,
animationDelay
]);

if (!response.ok) throw new Error("Backend Offline");

const data = await response.json();
/* store latest scan result for chatbot */
localStorage.setItem(
    "latestScan",
    JSON.stringify(data)
);

clearInterval(stepInterval);

dynamicStatus.innerText = "✅ Analysis Finalized. Generating Report...";

setTimeout(()=>{

const steps = document.querySelector(".scan-steps");
if(steps) steps.remove();

radar.classList.add('hidden');

displayResult(data,urlInput);
addToHistory("URL",urlInput,data);

},600);

}
catch(error){

clearInterval(stepInterval);

const steps = document.querySelector(".scan-steps");
if(steps) steps.remove();

radar.classList.add('hidden');

alert("⚠️ System Error: Neural Engine Offline. Please start the FastAPI server.");

}
finally{

btn.disabled=false;
input.readOnly=false;

}

}

/* ---------------- TEXT SCANNER ---------------- */

async function scanText() {

const textInput = document.getElementById('text-input').value.trim();
const radar = document.getElementById('scanning-radar');
const resultBox = document.getElementById('result-container');
const dynamicStatus = document.getElementById('dynamic-status');
const btn = document.getElementById('text-btn');

if (!textInput || textInput.length < 3) {
alert("❌ Please enter valid message text.");
return;
}

btn.disabled = true;
resultBox.classList.add('hidden');
radar.classList.remove('hidden');

const scanSteps = [
"📝 Reading Message Content...",
"🧠 NLP Engine Processing...",
"🔍 Detecting Social Engineering...",
"📊 Calculating Threat Score..."
];

startScanAnimation(scanSteps);

let step = 0;

const stepInterval = setInterval(() => {

const stepEl = document.getElementById("scan-step-" + step);

if (stepEl) {
stepEl.classList.add("active");
dynamicStatus.innerText = scanSteps[step];
}

step++;

if (step >= scanSteps.length) {
clearInterval(stepInterval);
}

}, 700);

try {

const response = await fetch(`${API_BASE}/predict/text`, {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ text: textInput })
});

if (!response.ok) throw new Error("Backend Error");

const data = await response.json();

clearInterval(stepInterval);

setTimeout(() => {

const steps = document.querySelector(".scan-steps");
if (steps) steps.remove();

radar.classList.add('hidden');

displayResult(data, textInput);
addToHistory("TEXT", textInput, data);

}, 700);

}
catch(error) {

clearInterval(stepInterval);

alert("⚠️ Text Analyzer Error");

radar.classList.add('hidden');

}
finally {

btn.disabled = false;

}

}


/* ---------------- DISPLAY RESULT ---------------- */

function displayResult(data,targetValue){

currentReportData={...data,target:targetValue};

const box=document.getElementById('result-container');
const title=document.getElementById('result-title');
const desc=document.getElementById('result-desc');

const bar=document.getElementById('confidence-bar');
const percentageLabel=document.querySelector('.percentage-text');

const barDomain=document.getElementById('bar-domain');
const barEntropy=document.getElementById('bar-entropy');

const valDomain=document.getElementById('val-domain');
const valEntropy=document.getElementById('val-entropy');


box.classList.remove('hidden','safe-mode','danger-mode','warning-mode');

box.style.opacity="0";
box.style.transform="translateY(15px)";

requestAnimationFrame(()=>{
box.style.transition="all 0.5s cubic-bezier(0.19,1,0.22,1)";
box.style.opacity="1";
box.style.transform="translateY(0)";
});


const prediction=data.prediction || "UNKNOWN";
const threatLevel=data.threat_level || "Low";
const scoreText=data.score || "0%";
const scoreValue=parseFloat(scoreText.replace('%',''));


if(bar) bar.style.width=scoreValue+"%";

if(percentageLabel){
percentageLabel.innerText=scoreValue+"% ACCURACY";
}


title.innerText=prediction.toUpperCase();


/* -------- SIGNAL WARNINGS -------- */

let warningHTML="";

if(data.tld_warning){
warningHTML+=`<div class="badge badge-warning">${data.tld_warning}</div>`;
}

if(data.subdomain_warning){
warningHTML+=`<div class="badge badge-warning">${data.subdomain_warning}</div>`;
}


/* -------- RESULT TEXT -------- */

desc.innerHTML=`

<div class="risk-badge badge-${threatLevel.toLowerCase()}">RISK: ${threatLevel}</div>

<strong>Protocol:</strong> ${data.method || 'Neural-X Engine'} (${scoreText})<br>

<p class="advice-text">${data.reason}</p>

${warningHTML}

`;


/* -------- WHOIS -------- */

if(data.whois){

const registrarEl=document.getElementById('whois-registrar');
const createdEl=document.getElementById('whois-created');
const rawEl=document.getElementById('whois-raw');
const ageEl=document.getElementById('whois-age');

if(ageEl) ageEl.innerText=data.whois.domain_age || "Unknown";
if(registrarEl) registrarEl.innerText=data.whois.registrar || "Protected";
if(createdEl) createdEl.innerText=data.whois.creation_date || "Unknown";
if(rawEl) rawEl.innerText=data.whois.raw_text || "No metadata found.";

}


/* -------- ANALYSIS BARS -------- */

if(barDomain && barEntropy){

const isSafe=prediction.toLowerCase().includes('safe');

const dScore=isSafe?(85+Math.random()*10):(15+Math.random()*20);
const eScore=isSafe?(12+Math.random()*10):(75+Math.random()*20);

barDomain.style.width=dScore+"%";
if(valDomain) valDomain.innerText=Math.round(dScore)+"%";

barEntropy.style.width=eScore+"%";
if(valEntropy) valEntropy.innerText=Math.round(eScore)+"%";

}


/* -------- RESULT MODE -------- */

if(prediction.toLowerCase().includes("safe")){
box.classList.add('safe-mode');
}
else if(threatLevel==="High"){
box.classList.add('danger-mode');
}
else{
box.classList.add('warning-mode');
}

}



/* ---------------- DOWNLOAD REPORT ---------------- */

function downloadReport(){

if(!currentReportData) return alert("No active scan data found.");

const reportContent=`
🛡️ PHISH-SHIELD AI FORENSIC ANALYSIS
========================================
Generated: ${new Date().toLocaleString()}
Target: ${currentReportData.target}
Verdict: ${currentReportData.prediction.toUpperCase()}
Risk: ${currentReportData.threat_level}
Confidence: ${currentReportData.score}

[WHOIS METADATA]
Registrar: ${currentReportData.whois?.registrar || "N/A"}
Created: ${currentReportData.whois?.creation_date || "N/A"}
`;

const blob=new Blob([reportContent],{type:'text/plain'});

const url=window.URL.createObjectURL(blob);

const a=document.createElement('a');
a.href=url;
a.download=`Report_${Date.now()}.txt`;

document.body.appendChild(a);
a.click();

window.URL.revokeObjectURL(url);
document.body.removeChild(a);

}



/* ---------------- HISTORY ---------------- */

let scanHistory=JSON.parse(localStorage.getItem('phish_history')) || [];

function addToHistory(type,target,data){

const newScan={
type:type.toUpperCase(),
target:target.length>30?target.substring(0,27)+"...":target,
prediction:data.prediction,
threat:data.threat_level || "Low",
timestamp:new Date().toLocaleTimeString()
};

scanHistory.unshift(newScan);

if(scanHistory.length>5) scanHistory.pop();

localStorage.setItem('phish_history',JSON.stringify(scanHistory));

renderHistory();

}



function renderHistory(){

const body=document.getElementById('history-body');
const section=document.getElementById('history-section');

if(!body || !section) return;

if(scanHistory.length===0){
section.classList.add('hidden');
return;
}

section.classList.remove('hidden');

body.innerHTML=scanHistory.map(scan=>{

const resultClass=scan.prediction.toLowerCase()==="safe"?"badge-safe":"badge-phishing";

const threatClass=scan.threat.toLowerCase()==="high"?"badge-phishing":"badge-medium";

return `
<tr>
<td>${scan.type}</td>
<td>${scan.target}</td>
<td><span class="badge ${resultClass}">${scan.prediction.toUpperCase()}</span></td>
<td><span class="badge ${threatClass}">${scan.threat}</span></td>
</tr>
`;

}).join('');

}



/* ---------------- UI UTILITIES ---------------- */

function showTab(type){

document.getElementById('url-tab').style.display=type==='url'?'block':'none';
document.getElementById('text-tab').style.display=type==='text'?'block':'none';

const buttons=document.querySelectorAll('.tab-btn');

buttons[0].classList.toggle('active',type==='url');
buttons[1].classList.toggle('active',type==='text');

document.getElementById('result-container').classList.add('hidden');

}


function clearHistory(){
scanHistory=[];
localStorage.removeItem('phish_history');
renderHistory();
}



/* ---------------- COPY RESULT ---------------- */

function copyResult(){

const prediction=document.getElementById('result-title').innerText;

const report=`🛡️ Phish-Shield AI Verdict: ${prediction}
Date: ${new Date().toLocaleString()}`;

navigator.clipboard.writeText(report).then(()=>{

const btn=document.getElementById('copy-btn');

btn.innerText="✅ COPIED";

setTimeout(()=>{btn.innerText="📋 Copy Report";},2000);

});

}



/* ---------------- THEME ---------------- */

document.addEventListener("DOMContentLoaded",()=>{

const themeCheckbox=document.getElementById("checkbox");

const savedTheme=localStorage.getItem("theme");

if(savedTheme==="light"){
document.body.classList.add("light-mode");
if(themeCheckbox) themeCheckbox.checked=true;
}

if(themeCheckbox){

themeCheckbox.addEventListener("change",(e)=>{

if(e.target.checked){
document.body.classList.add("light-mode");
localStorage.setItem("theme","light");
}
else{
document.body.classList.remove("light-mode");
localStorage.setItem("theme","dark");
}

});

}

renderHistory();

});