0000000000001240 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	test   %rcx,%rcx
    124d:	je     1354 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x114>
    1253:	mov    (%rsi),%rax
    1256:	mov    0x8(%rsi),%rsi
    125a:	mov    %rax,-0x8(%rsp)
    125f:	sub    %rax,%rsi
    1262:	sar    $0x2,%rsi
    1266:	lea    0x0(,%rcx,4),%rax
    126e:	mov    %rax,-0x20(%rsp)
    1273:	xor    %r9d,%r9d
    1276:	xor    %r10d,%r10d
    1279:	xor    %ebx,%ebx
    127b:	mov    %rdx,-0x18(%rsp)
    1280:	mov    %rbx,-0x10(%rsp)
    1285:	imul   %rcx,%rbx
    1289:	mov    (%rdx),%r14
    128c:	mov    0x8(%rdx),%r15
    1290:	sub    %r14,%r15
    1293:	sar    $0x2,%r15
    1297:	xor    %r12d,%r12d
    129a:	xor    %r13d,%r13d
    129d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ac:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bb:	nopl   0x0(%rax,%rax,1)
    12c0:	lea    (%rbx,%r13,1),%rax
    12c4:	cmp    %rax,%rsi
    12c7:	jbe    135f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x11f>
    12cd:	mov    -0x8(%rsp),%rdx
    12d2:	mov    (%rdx,%rax,4),%ebp
    12d5:	mov    (%rdi),%r11
    12d8:	mov    0x8(%rdi),%rdx
    12dc:	sub    %r11,%rdx
    12df:	sar    $0x2,%rdx
    12e3:	add    %r10,%r11
    12e6:	xor    %eax,%eax
    12e8:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f7:	nopw   0x0(%rax,%rax,1)
    1300:	lea    (%r12,%rax,1),%r8
    1304:	cmp    %r8,%r15
    1307:	jbe    135f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x11f>
    1309:	lea    (%r9,%rax,1),%r8
    130d:	cmp    %r8,%rdx
    1310:	jbe    135f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x11f>
    1312:	mov    (%r14,%rax,4),%r8d
    1316:	imul   %ebp,%r8d
    131a:	add    %r8d,(%r11,%rax,4)
    131e:	inc    %rax
    1321:	cmp    %rax,%rcx
    1324:	jne    1300 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    1326:	inc    %r13
    1329:	add    -0x20(%rsp),%r14
    132e:	add    %rcx,%r12
    1331:	cmp    %rcx,%r13
    1334:	jne    12c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1336:	mov    -0x10(%rsp),%rbx
    133b:	inc    %rbx
    133e:	add    -0x20(%rsp),%r10
    1343:	add    %rcx,%r9
    1346:	cmp    %rcx,%rbx
    1349:	mov    -0x18(%rsp),%rdx
    134e:	jne    1280 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x40>
    1354:	pop    %rbx
    1355:	pop    %r12
    1357:	pop    %r13
    1359:	pop    %r14
    135b:	pop    %r15
    135d:	pop    %rbp
    135e:	ret
    135f:	ud2
    1361:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
