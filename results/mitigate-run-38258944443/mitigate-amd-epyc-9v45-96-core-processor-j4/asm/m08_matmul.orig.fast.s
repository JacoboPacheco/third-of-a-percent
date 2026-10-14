0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	test   %rcx,%rcx
    124d:	je     1324 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xe4>
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
    129d:	nopl   (%rax)
    12a0:	lea    (%rbx,%r13,1),%rax
    12a4:	cmp    %rax,%rsi
    12a7:	jbe    132f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xef>
    12ad:	mov    -0x8(%rsp),%rdx
    12b2:	mov    (%rdx,%rax,4),%ebp
    12b5:	mov    (%rdi),%r11
    12b8:	mov    0x8(%rdi),%rdx
    12bc:	sub    %r11,%rdx
    12bf:	sar    $0x2,%rdx
    12c3:	add    %r10,%r11
    12c6:	xor    %eax,%eax
    12c8:	nopl   0x0(%rax,%rax,1)
    12d0:	lea    (%r12,%rax,1),%r8
    12d4:	cmp    %r8,%r15
    12d7:	jbe    132f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xef>
    12d9:	lea    (%r9,%rax,1),%r8
    12dd:	cmp    %r8,%rdx
    12e0:	jbe    132f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xef>
    12e2:	mov    (%r14,%rax,4),%r8d
    12e6:	imul   %ebp,%r8d
    12ea:	add    %r8d,(%r11,%rax,4)
    12ee:	inc    %rax
    12f1:	cmp    %rax,%rcx
    12f4:	jne    12d0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x90>
    12f6:	inc    %r13
    12f9:	add    -0x20(%rsp),%r14
    12fe:	add    %rcx,%r12
    1301:	cmp    %rcx,%r13
    1304:	jne    12a0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x60>
    1306:	mov    -0x10(%rsp),%rbx
    130b:	inc    %rbx
    130e:	add    -0x20(%rsp),%r10
    1313:	add    %rcx,%r9
    1316:	cmp    %rcx,%rbx
    1319:	mov    -0x18(%rsp),%rdx
    131e:	jne    1280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x40>
    1324:	pop    %rbx
    1325:	pop    %r12
    1327:	pop    %r13
    1329:	pop    %r14
    132b:	pop    %r15
    132d:	pop    %rbp
    132e:	ret
    132f:	ud2
    1331:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
