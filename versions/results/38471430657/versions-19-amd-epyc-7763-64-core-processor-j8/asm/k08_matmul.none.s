0000000000001220 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1220:	test   %rcx,%rcx
    1223:	je     1452 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x232>
    1229:	push   %rbp
    122a:	push   %r15
    122c:	push   %r14
    122e:	push   %r13
    1230:	push   %r12
    1232:	push   %rbx
    1233:	mov    (%rsi),%rax
    1236:	mov    %rax,-0x18(%rsp)
    123b:	mov    (%rdx),%rdx
    123e:	mov    (%rdi),%r12
    1241:	lea    0x0(,%rcx,4),%rdi
    1249:	mov    %rcx,%rax
    124c:	imul   %rcx,%rax
    1250:	lea    (%rdx,%rax,4),%rax
    1254:	mov    %rax,-0x28(%rsp)
    1259:	lea    (%r12,%rcx,4),%rax
    125d:	mov    %rax,-0x30(%rsp)
    1262:	mov    %rcx,%r10
    1265:	and    $0xfffffffffffffff8,%r10
    1269:	lea    -0x1(%rcx),%r11
    126d:	mov    %rdx,-0x40(%rsp)
    1272:	lea    0x10(%rdx),%rax
    1276:	mov    %rax,-0x38(%rsp)
    127b:	lea    0x10(%r12),%r14
    1280:	xor    %r8d,%r8d
    1283:	mov    %r12,-0x20(%rsp)
    1288:	jmp    12a7 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x87>
    128a:	nopw   0x0(%rax,%rax,1)
    1290:	mov    -0x10(%rsp),%r8
    1295:	inc    %r8
    1298:	add    %rdi,%r14
    129b:	add    %rdi,%r12
    129e:	cmp    %rcx,%r8
    12a1:	je     1448 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x228>
    12a7:	test   %rdi,%rdi
    12aa:	sets   %dl
    12ad:	mov    %rdi,%rax
    12b0:	imul   %r8,%rax
    12b4:	mov    -0x20(%rsp),%rbx
    12b9:	lea    (%rbx,%rax,1),%rsi
    12bd:	add    -0x30(%rsp),%rax
    12c2:	mov    %r8,-0x10(%rsp)
    12c7:	imul   %rcx,%r8
    12cb:	mov    -0x18(%rsp),%r9
    12d0:	lea    (%r9,%r8,4),%r13
    12d4:	lea    (%rbx,%r8,4),%r8
    12d8:	mov    %r8,-0x8(%rsp)
    12dd:	cmp    -0x28(%rsp),%rsi
    12e2:	setb   %sil
    12e6:	mov    -0x40(%rsp),%r8
    12eb:	cmp    %rax,%r8
    12ee:	setb   %al
    12f1:	and    %sil,%al
    12f4:	or     %dl,%al
    12f6:	mov    %r8,%rdx
    12f9:	mov    -0x38(%rsp),%rbx
    12fe:	xor    %r9d,%r9d
    1301:	jmp    1322 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x102>
    1303:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1310:	inc    %r9
    1313:	add    %rdi,%rbx
    1316:	add    %rdi,%rdx
    1319:	cmp    %rcx,%r9
    131c:	je     1290 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    1322:	cmp    $0x8,%rcx
    1326:	setb   %r8b
    132a:	mov    0x0(%r13,%r9,4),%esi
    132f:	or     %al,%r8b
    1332:	test   $0x1,%r8b
    1336:	je     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x120>
    1338:	xor    %r8d,%r8d
    133b:	jmp    13da <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1ba>
    1340:	movd   %esi,%xmm0
    1344:	pshufd $0x0,%xmm0,%xmm0
    1349:	pshufd $0xf5,%xmm0,%xmm1
    134e:	xor    %r15d,%r15d
    1351:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1360:	movdqu -0x10(%rbx,%r15,4),%xmm2
    1367:	movdqu (%rbx,%r15,4),%xmm3
    136d:	pshufd $0xf5,%xmm2,%xmm4
    1372:	pmuludq %xmm0,%xmm2
    1376:	pshufd $0xe8,%xmm2,%xmm2
    137b:	pmuludq %xmm1,%xmm4
    137f:	pshufd $0xe8,%xmm4,%xmm4
    1384:	punpckldq %xmm4,%xmm2
    1388:	pshufd $0xf5,%xmm3,%xmm4
    138d:	pmuludq %xmm0,%xmm3
    1391:	pshufd $0xe8,%xmm3,%xmm3
    1396:	pmuludq %xmm1,%xmm4
    139a:	pshufd $0xe8,%xmm4,%xmm4
    139f:	punpckldq %xmm4,%xmm3
    13a3:	movdqu -0x10(%r14,%r15,4),%xmm4
    13aa:	paddd  %xmm2,%xmm4
    13ae:	movdqu (%r14,%r15,4),%xmm2
    13b4:	paddd  %xmm3,%xmm2
    13b8:	movdqu %xmm4,-0x10(%r14,%r15,4)
    13bf:	movdqu %xmm2,(%r14,%r15,4)
    13c5:	add    $0x8,%r15
    13c9:	cmp    %r15,%r10
    13cc:	jne    1360 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    13ce:	mov    %r10,%r8
    13d1:	cmp    %rcx,%r10
    13d4:	je     1310 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    13da:	mov    %r8,%r15
    13dd:	test   $0x1,%cl
    13e0:	je     1412 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1f2>
    13e2:	mov    %r9,%r15
    13e5:	imul   %rcx,%r15
    13e9:	mov    -0x40(%rsp),%rbp
    13ee:	lea    0x0(,%r15,4),%r15
    13f6:	add    %rbp,%r15
    13f9:	mov    (%r15,%r8,4),%r15d
    13fd:	imul   %esi,%r15d
    1401:	mov    -0x8(%rsp),%rbp
    1406:	add    %r15d,0x0(%rbp,%r8,4)
    140b:	mov    %r8,%r15
    140e:	or     $0x1,%r15
    1412:	cmp    %r11,%r8
    1415:	je     1310 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    141b:	nopl   0x0(%rax,%rax,1)
    1420:	mov    (%rdx,%r15,4),%r8d
    1424:	imul   %esi,%r8d
    1428:	add    %r8d,(%r12,%r15,4)
    142c:	mov    0x4(%rdx,%r15,4),%r8d
    1431:	imul   %esi,%r8d
    1435:	add    %r8d,0x4(%r12,%r15,4)
    143a:	add    $0x2,%r15
    143e:	cmp    %r15,%rcx
    1441:	jne    1420 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    1443:	jmp    1310 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    1448:	pop    %rbx
    1449:	pop    %r12
    144b:	pop    %r13
    144d:	pop    %r14
    144f:	pop    %r15
    1451:	pop    %rbp
    1452:	ret
    1453:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
