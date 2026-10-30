0000000000001240 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1318 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd8>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdi),%rdx
    1257:	mov    0x8(%rdi),%rsi
    125b:	sub    %rdx,%rsi
    125e:	sar    $0x2,%rsi
    1262:	cmp    $0x1,%rcx
    1266:	adc    $0x0,%rcx
    126a:	lea    -0x1(%rcx),%r8
    126e:	cmp    %rsi,%r8
    1271:	cmovae %rsi,%r8
    1275:	xor    %edi,%edi
    1277:	cmp    $0x8,%r8
    127b:	jb     1300 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1281:	mov    %rdx,%r9
    1284:	sub    %rax,%r9
    1287:	cmp    $0x1f,%r9
    128b:	jbe    1300 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    128d:	inc    %r8
    1290:	mov    %r8d,%edi
    1293:	and    $0x7,%edi
    1296:	mov    $0x8,%r9d
    129c:	cmovne %rdi,%r9
    12a0:	mov    %r8,%rdi
    12a3:	sub    %r9,%rdi
    12a6:	xor    %r8d,%r8d
    12a9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b8:	nopl   0x0(%rax,%rax,1)
    12c0:	movdqu (%rax,%r8,4),%xmm0
    12c6:	movdqu 0x10(%rax,%r8,4),%xmm1
    12cd:	paddd  %xmm0,%xmm0
    12d1:	paddd  %xmm1,%xmm1
    12d5:	movdqu %xmm0,(%rdx,%r8,4)
    12db:	movdqu %xmm1,0x10(%rdx,%r8,4)
    12e2:	add    $0x8,%r8
    12e6:	cmp    %r8,%rdi
    12e9:	jne    12c0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12eb:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fa:	nopw   0x0(%rax,%rax,1)
    1300:	cmp    %rdi,%rsi
    1303:	je     1319 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd9>
    1305:	mov    (%rax,%rdi,4),%r8d
    1309:	add    %r8d,%r8d
    130c:	mov    %r8d,(%rdx,%rdi,4)
    1310:	inc    %rdi
    1313:	cmp    %rdi,%rcx
    1316:	jne    1300 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1318:	ret
    1319:	ud2
    131b:	nopl   0x0(%rax,%rax,1)
