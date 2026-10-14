0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	mov    %rdx,%r8
    124d:	mov    %rcx,%rax
    1250:	mul    %rcx
    1253:	jo     1336 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf6>
    1259:	mov    (%rsi),%rdx
    125c:	mov    0x8(%rsi),%rsi
    1260:	sub    %rdx,%rsi
    1263:	sar    $0x2,%rsi
    1267:	cmp    %rax,%rsi
    126a:	jb     1336 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf6>
    1270:	mov    (%r8),%r12
    1273:	mov    0x8(%r8),%r8
    1277:	sub    %r12,%r8
    127a:	sar    $0x2,%r8
    127e:	cmp    %rax,%r8
    1281:	jb     1336 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf6>
    1287:	mov    (%rdi),%r10
    128a:	mov    0x8(%rdi),%rdi
    128e:	sub    %r10,%rdi
    1291:	sar    $0x2,%rdi
    1295:	cmp    %rax,%rdi
    1298:	jb     1336 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf6>
    129e:	test   %rcx,%rcx
    12a1:	je     132b <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xeb>
    12a7:	lea    0x0(,%rcx,4),%rax
    12af:	xor    %r11d,%r11d
    12b2:	xor    %r14d,%r14d
    12b5:	mov    %r12,-0x10(%rsp)
    12ba:	mov    %r14,-0x8(%rsp)
    12bf:	imul   %rcx,%r14
    12c3:	xor    %r15d,%r15d
    12c6:	xor    %r13d,%r13d
    12c9:	nopl   0x0(%rax)
    12d0:	lea    (%r14,%r13,1),%r9
    12d4:	cmp    %r9,%rsi
    12d7:	jbe    1336 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf6>
    12d9:	mov    (%rdx,%r9,4),%ebp
    12dd:	xor    %r9d,%r9d
    12e0:	lea    (%r15,%r9,1),%rbx
    12e4:	cmp    %rbx,%r8
    12e7:	jbe    1336 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf6>
    12e9:	lea    (%r11,%r9,1),%rbx
    12ed:	cmp    %rbx,%rdi
    12f0:	jbe    1336 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf6>
    12f2:	mov    (%r12,%r9,4),%ebx
    12f6:	imul   %ebp,%ebx
    12f9:	add    %ebx,(%r10,%r9,4)
    12fd:	inc    %r9
    1300:	cmp    %r9,%rcx
    1303:	jne    12e0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xa0>
    1305:	inc    %r13
    1308:	add    %rax,%r12
    130b:	add    %rcx,%r15
    130e:	cmp    %rcx,%r13
    1311:	jne    12d0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x90>
    1313:	mov    -0x8(%rsp),%r14
    1318:	inc    %r14
    131b:	add    %rax,%r10
    131e:	add    %rcx,%r11
    1321:	cmp    %rcx,%r14
    1324:	mov    -0x10(%rsp),%r12
    1329:	jne    12ba <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x7a>
    132b:	pop    %rbx
    132c:	pop    %r12
    132e:	pop    %r13
    1330:	pop    %r14
    1332:	pop    %r15
    1334:	pop    %rbp
    1335:	ret
    1336:	ud2
    1338:	nopl   0x0(%rax,%rax,1)
