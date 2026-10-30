0000000000001220 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
    1220:	test   %rdx,%rdx
    1223:	je     12cd <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xad>
    1229:	mov    (%rsi),%rax
    122c:	mov    0x8(%rsi),%rcx
    1230:	sub    %rax,%rcx
    1233:	sar    $0x2,%rcx
    1237:	mov    (%rdi),%rsi
    123a:	mov    0x8(%rdi),%rdi
    123e:	sub    %rsi,%rdi
    1241:	sar    $0x2,%rdi
    1245:	lea    -0x1(%rdx),%r8
    1249:	cmp    %r8,%rdi
    124c:	cmovb  %rdi,%r8
    1250:	cmp    %rcx,%r8
    1253:	cmovae %rcx,%r8
    1257:	inc    %r8
    125a:	xor    %r9d,%r9d
    125d:	cmp    $0x5,%r8
    1261:	jb     12b0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x90>
    1263:	mov    %rsi,%r10
    1266:	sub    %rax,%r10
    1269:	cmp    $0xf,%r10
    126d:	jbe    12b0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x90>
    126f:	mov    %r8d,%r9d
    1272:	and    $0x3,%r9d
    1276:	mov    $0x4,%r10d
    127c:	cmovne %r9,%r10
    1280:	sub    %r10,%r8
    1283:	xor    %r9d,%r9d
    1286:	cs nopw 0x0(%rax,%rax,1)
    1290:	movdqu (%rax,%r9,4),%xmm0
    1296:	paddd  %xmm0,%xmm0
    129a:	movdqu %xmm0,(%rsi,%r9,4)
    12a0:	add    $0x4,%r9
    12a4:	cmp    %r9,%r8
    12a7:	jne    1290 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x70>
    12a9:	mov    %r8,%r9
    12ac:	nopl   0x0(%rax)
    12b0:	cmp    %r9,%rcx
    12b3:	je     12ce <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xae>
    12b5:	cmp    %r9,%rdi
    12b8:	je     12ce <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xae>
    12ba:	mov    (%rax,%r9,4),%r8d
    12be:	add    %r8d,%r8d
    12c1:	mov    %r8d,(%rsi,%r9,4)
    12c5:	inc    %r9
    12c8:	cmp    %r9,%rdx
    12cb:	jne    12b0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x90>
    12cd:	ret
    12ce:	ud2
