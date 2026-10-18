0000000000001220 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1220:	push   %rbp
    1221:	push   %r15
    1223:	push   %r14
    1225:	push   %r13
    1227:	push   %r12
    1229:	push   %rbx
    122a:	test   %rcx,%rcx
    122d:	je     1304 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xe4>
    1233:	mov    (%rsi),%rax
    1236:	mov    0x8(%rsi),%rsi
    123a:	mov    %rax,-0x8(%rsp)
    123f:	sub    %rax,%rsi
    1242:	sar    $0x2,%rsi
    1246:	lea    0x0(,%rcx,4),%rax
    124e:	mov    %rax,-0x20(%rsp)
    1253:	xor    %r9d,%r9d
    1256:	xor    %r10d,%r10d
    1259:	xor    %ebx,%ebx
    125b:	mov    %rdx,-0x18(%rsp)
    1260:	mov    %rbx,-0x10(%rsp)
    1265:	imul   %rcx,%rbx
    1269:	mov    (%rdx),%r14
    126c:	mov    0x8(%rdx),%r15
    1270:	sub    %r14,%r15
    1273:	sar    $0x2,%r15
    1277:	xor    %r12d,%r12d
    127a:	xor    %r13d,%r13d
    127d:	nopl   (%rax)
    1280:	lea    (%rbx,%r13,1),%rax
    1284:	cmp    %rax,%rsi
    1287:	jbe    130f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xef>
    128d:	mov    -0x8(%rsp),%rdx
    1292:	mov    (%rdx,%rax,4),%ebp
    1295:	mov    (%rdi),%r11
    1298:	mov    0x8(%rdi),%rdx
    129c:	sub    %r11,%rdx
    129f:	sar    $0x2,%rdx
    12a3:	add    %r10,%r11
    12a6:	xor    %eax,%eax
    12a8:	nopl   0x0(%rax,%rax,1)
    12b0:	lea    (%r12,%rax,1),%r8
    12b4:	cmp    %r8,%r15
    12b7:	jbe    130f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xef>
    12b9:	lea    (%r9,%rax,1),%r8
    12bd:	cmp    %r8,%rdx
    12c0:	jbe    130f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xef>
    12c2:	mov    (%r14,%rax,4),%r8d
    12c6:	imul   %ebp,%r8d
    12ca:	add    %r8d,(%r11,%rax,4)
    12ce:	inc    %rax
    12d1:	cmp    %rax,%rcx
    12d4:	jne    12b0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x90>
    12d6:	inc    %r13
    12d9:	add    -0x20(%rsp),%r14
    12de:	add    %rcx,%r12
    12e1:	cmp    %rcx,%r13
    12e4:	jne    1280 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x60>
    12e6:	mov    -0x10(%rsp),%rbx
    12eb:	inc    %rbx
    12ee:	add    -0x20(%rsp),%r10
    12f3:	add    %rcx,%r9
    12f6:	cmp    %rcx,%rbx
    12f9:	mov    -0x18(%rsp),%rdx
    12fe:	jne    1260 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x40>
    1304:	pop    %rbx
    1305:	pop    %r12
    1307:	pop    %r13
    1309:	pop    %r14
    130b:	pop    %r15
    130d:	pop    %rbp
    130e:	ret
    130f:	ud2
    1311:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
