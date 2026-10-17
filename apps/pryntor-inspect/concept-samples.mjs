// Original disposable demonstration projects, no invented historical customer data.
export const CONCEPT_SAMPLES=Object.freeze({
  web:[
    {name:'web-app/main.ts',text:'import { format } from "./utils";\nimport { profile } from "./profile";\nexport function show() { return format(profile.name); }\n'},
    {name:'web-app/utils.ts',text:'export function format(value) { return String(value).trim(); }\n'},
    {name:'web-app/profile.ts',text:'export const profile = { name: "Ari" };\n// TODO: add display formatting tests\n'}
  ],
  mobile:[
    {name:'mobile-ui/App.tsx',text:'import { Card } from "./Card";\nexport function App() { return Card({title:"Welcome"}); }\n'},
    {name:'mobile-ui/Card.tsx',text:'export function Card({title}) { return title; }\n'}
  ],
  marketing:[
    {name:'marketing-site/index.js',text:'import { heading } from "./content";\nexport function renderPage() { return heading; }\n'},
    {name:'marketing-site/content.js',text:'export const heading = "Build something clear";\n// TODO: check heading contrast\n'}
  ]
});

