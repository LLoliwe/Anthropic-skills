import test from 'node:test';
import assert from 'node:assert/strict';
import { calculate, GRAVITY, K_N_PER_M } from '../model.mjs';

test('no mass: zero force and zero spring extension',()=>{
 const x=calculate(0); assert.equal(x.forceN,0);assert.equal(x.extensionMm,0);
});
test('1 kg: 9.81 N; 24.525 mm',()=>{
 const x=calculate(1000);assert.equal(x.forceN,9.81);assert.ok(Math.abs(x.extensionMm-24.525)<1e-10);
});
test('2 kg: 19.62 N; 49.05 mm',()=>{
 const x=calculate(2000);assert.equal(x.forceN,19.62);assert.ok(Math.abs(x.extensionMm-49.05)<1e-10);
});
test('linearity and Hooke force balance over all user steps',()=>{
 for(let g=0;g<=2000;g+=100){const x=calculate(g);assert.ok(Math.abs(x.k*x.extensionM-x.forceN)<1e-12);assert.ok(Math.abs(x.forceN-x.massKg*GRAVITY)<1e-12);}
});
test('reject impossible readings and invalid constants',()=>{
 for(const g of [-1,2001,NaN,Infinity])assert.throws(()=>calculate(g),RangeError);
 for(const k of [0,-1,NaN])assert.throws(()=>calculate(100,k),RangeError);
});
test('model outputs immutable state',()=>assert.ok(Object.isFrozen(calculate(500))));