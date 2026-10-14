0000000000001220 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rdx
    1227:	sub    %rax,%rdx
    122a:	je     1378 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x158>
    1230:	sar    $0x2,%rdx
    1234:	mov    (%rdi),%rcx
    1237:	cmp    $0x20,%rdx
    123b:	jb     12d9 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    1241:	mov    %rax,%rsi
    1244:	sub    %rcx,%rsi
    1247:	cmp    $0x80,%rsi
    124e:	jb     12d9 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    1254:	mov    %rdx,%rdi
    1257:	and    $0xffffffffffffffe0,%rdi
    125b:	mov    %edx,%esi
    125d:	and    $0x1f,%esi
    1260:	lea    (%rax,%rdx,4),%r8
    1264:	add    $0xffffffffffffffe0,%r8
    1268:	lea    (%rcx,%rdx,4),%r9
    126c:	add    $0xffffffffffffffe0,%r9
    1270:	mov    %rdi,%r10
    1273:	neg    %r10
    1276:	xor    %r11d,%r11d
    1279:	nopl   0x0(%rax)
    1280:	vmovdqu -0x60(%r8,%r11,4),%ymm0
    1287:	vmovdqu -0x40(%r8,%r11,4),%ymm1
    128e:	vmovdqu -0x20(%r8,%r11,4),%ymm2
    1295:	vmovdqu (%r8,%r11,4),%ymm3
    129b:	vpaddd %ymm3,%ymm3,%ymm3
    129f:	vpaddd %ymm2,%ymm2,%ymm2
    12a3:	vpaddd %ymm1,%ymm1,%ymm1
    12a7:	vpaddd %ymm0,%ymm0,%ymm0
    12ab:	vmovdqu %ymm3,(%r9,%r11,4)
    12b1:	vmovdqu %ymm2,-0x20(%r9,%r11,4)
    12b8:	vmovdqu %ymm1,-0x40(%r9,%r11,4)
    12bf:	vmovdqu %ymm0,-0x60(%r9,%r11,4)
    12c6:	add    $0xffffffffffffffe0,%r11
    12ca:	cmp    %r11,%r10
    12cd:	jne    1280 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    12cf:	cmp    %rdi,%rdx
    12d2:	jne    12dc <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xbc>
    12d4:	jmp    1378 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x158>
    12d9:	mov    %rdx,%rsi
    12dc:	lea    -0x1(%rsi),%rdi
    12e0:	mov    %rsi,%r8
    12e3:	and    $0x7,%r8
    12e7:	je     1311 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf1>
    12e9:	nopl   0x0(%rax)
    12f0:	lea    -0x1(%rsi),%rdx
    12f4:	mov    -0x4(%rax,%rsi,4),%r9d
    12f9:	add    %r9d,%r9d
    12fc:	mov    %r9d,-0x4(%rcx,%rsi,4)
    1301:	mov    %rdx,%rsi
    1304:	dec    %r8
    1307:	jne    12f0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd0>
    1309:	cmp    $0x7,%rdi
    130d:	jae    131a <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xfa>
    130f:	jmp    1378 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x158>
    1311:	mov    %rsi,%rdx
    1314:	cmp    $0x7,%rdi
    1318:	jb     1378 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x158>
    131a:	dec    %rdx
    131d:	nopl   (%rax)
    1320:	mov    (%rax,%rdx,4),%esi
    1323:	add    %esi,%esi
    1325:	mov    %esi,(%rcx,%rdx,4)
    1328:	mov    -0x4(%rax,%rdx,4),%esi
    132c:	add    %esi,%esi
    132e:	mov    %esi,-0x4(%rcx,%rdx,4)
    1332:	mov    -0x8(%rax,%rdx,4),%esi
    1336:	add    %esi,%esi
    1338:	mov    %esi,-0x8(%rcx,%rdx,4)
    133c:	mov    -0xc(%rax,%rdx,4),%esi
    1340:	add    %esi,%esi
    1342:	mov    %esi,-0xc(%rcx,%rdx,4)
    1346:	mov    -0x10(%rax,%rdx,4),%esi
    134a:	add    %esi,%esi
    134c:	mov    %esi,-0x10(%rcx,%rdx,4)
    1350:	mov    -0x14(%rax,%rdx,4),%esi
    1354:	add    %esi,%esi
    1356:	mov    %esi,-0x14(%rcx,%rdx,4)
    135a:	mov    -0x18(%rax,%rdx,4),%esi
    135e:	add    %esi,%esi
    1360:	mov    %esi,-0x18(%rcx,%rdx,4)
    1364:	mov    -0x1c(%rax,%rdx,4),%esi
    1368:	add    %esi,%esi
    136a:	mov    %esi,-0x1c(%rcx,%rdx,4)
    136e:	add    $0xfffffffffffffff8,%rdx
    1372:	cmp    $0xffffffffffffffff,%rdx
    1376:	jne    1320 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1378:	vzeroupper
    137b:	ret
    137c:	nopl   0x0(%rax)
