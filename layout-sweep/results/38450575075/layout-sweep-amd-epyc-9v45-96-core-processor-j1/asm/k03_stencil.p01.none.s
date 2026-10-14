0000000000001230 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1230:	mov    (%rsi),%rax
    1233:	mov    0x8(%rsi),%r10
    1237:	mov    %r10,%r9
    123a:	sub    %rax,%r9
    123d:	mov    %r9,%rcx
    1240:	sar    $0x2,%rcx
    1244:	cmp    $0x3,%rcx
    1248:	jb     1367 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    124e:	mov    (%rdi),%rdx
    1251:	lea    -0x2(%rcx),%r8
    1255:	mov    $0x1,%edi
    125a:	mov    $0x2,%esi
    125f:	cmp    $0x8,%r8
    1263:	jb     12e9 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    1269:	lea    0x4(%rdx),%r11
    126d:	cmp    %r10,%r11
    1270:	jae    127e <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    1272:	add    %rdx,%r9
    1275:	add    $0xfffffffffffffffc,%r9
    1279:	cmp    %r9,%rax
    127c:	jb     12e9 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    127e:	mov    %r8,%r9
    1281:	and    $0xfffffffffffffff8,%r9
    1285:	lea    0x2(%r9),%rsi
    1289:	lea    0x1(%r9),%rdi
    128d:	xor    %r10d,%r10d
    1290:	movdqu (%rax,%r10,4),%xmm0
    1296:	movdqu 0x4(%rax,%r10,4),%xmm1
    129d:	paddd  %xmm0,%xmm1
    12a1:	movdqu 0x8(%rax,%r10,4),%xmm0
    12a8:	paddd  %xmm1,%xmm0
    12ac:	movdqu 0x10(%rax,%r10,4),%xmm1
    12b3:	movdqu 0x14(%rax,%r10,4),%xmm2
    12ba:	paddd  %xmm1,%xmm2
    12be:	movdqu 0x18(%rax,%r10,4),%xmm1
    12c5:	paddd  %xmm2,%xmm1
    12c9:	movdqu %xmm0,0x4(%rdx,%r10,4)
    12d0:	movdqu %xmm1,0x14(%rdx,%r10,4)
    12d7:	add    $0x8,%r10
    12db:	cmp    %r10,%r9
    12de:	jne    1290 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    12e0:	cmp    %r9,%r8
    12e3:	je     1367 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    12e9:	mov    %ecx,%r8d
    12ec:	sub    %esi,%r8d
    12ef:	lea    0x1(%rsi),%r9
    12f3:	test   $0x1,%r8b
    12f7:	jne    1306 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd6>
    12f9:	mov    %rsi,%r8
    12fc:	mov    %rdi,%rsi
    12ff:	cmp    %r9,%rcx
    1302:	jne    131f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xef>
    1304:	jmp    1367 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1306:	mov    (%rax,%rdi,4),%r8d
    130a:	add    -0x4(%rax,%rdi,4),%r8d
    130f:	add    (%rax,%rsi,4),%r8d
    1313:	mov    %r8d,(%rdx,%rdi,4)
    1317:	mov    %r9,%r8
    131a:	cmp    %r9,%rcx
    131d:	je     1367 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    131f:	neg    %rcx
    1322:	inc    %r8
    1325:	data16 cs nopw 0x0(%rax,%rax,1)
    1330:	mov    (%rax,%rsi,4),%edi
    1333:	add    -0x4(%rax,%rsi,4),%edi
    1337:	add    -0x4(%rax,%r8,4),%edi
    133c:	mov    %edi,(%rdx,%rsi,4)
    133f:	mov    -0x4(%rax,%r8,4),%esi
    1344:	add    -0x8(%rax,%r8,4),%esi
    1349:	add    (%rax,%r8,4),%esi
    134d:	mov    %esi,-0x4(%rdx,%r8,4)
    1352:	lea    (%rcx,%r8,1),%rdi
    1356:	add    $0x2,%rdi
    135a:	mov    %r8,%rsi
    135d:	add    $0x2,%r8
    1361:	cmp    $0x1,%rdi
    1365:	jne    1330 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1367:	ret
    1368:	nopl   0x0(%rax,%rax,1)
