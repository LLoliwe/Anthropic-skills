import {mkdirSync,copyFileSync,cpSync,rmSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url)),dist=path.join(root,'dist');
rmSync(dist,{recursive:true,force:true});mkdirSync(dist,{recursive:true});copyFileSync(path.join(root,'index.html'),path.join(dist,'index.html'));cpSync(path.join(root,'science'),path.join(dist,'science'),{recursive:true});
const water=path.resolve(root,'../lvl7-water-game-v1-1'),destination=path.join(dist,'apps/lvl7-water-game-v1-1');mkdirSync(destination,{recursive:true});for(const file of ['index.html','curriculum.html','curriculum.css','curriculum.mjs'])copyFileSync(path.join(water,file),path.join(destination,file));
const graphDestination=path.join(dist,'tools/learning-graph');mkdirSync(graphDestination,{recursive:true});copyFileSync(path.resolve(root,'../../tools/learning-graph/graph.mjs'),path.join(graphDestination,'graph.mjs'));
console.log('Built existing LVL7 science playground with canonical Water Lab and graph utility.');
