0000000000001220 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rsi
    1227:	sub    %rax,%rsi
    122a:	je     1314 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    1230:	sar    $0x2,%rsi
    1234:	mov    (%rdi),%rcx
    1237:	cmp    $0x8,%rsi
    123b:	setb   %dl
    123e:	mov    %rax,%rdi
    1241:	sub    %rcx,%rdi
    1244:	cmp    $0x20,%rdi
    1248:	setb   %dil
    124c:	or     %dl,%dil
    124f:	cmp    $0x1,%dil
    1253:	jne    125a <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3a>
    1255:	mov    %rsi,%rdx
    1258:	jmp    12b0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>
    125a:	mov    %rsi,%rdi
    125d:	and    $0xfffffffffffffff8,%rdi
    1261:	mov    %esi,%edx
    1263:	and    $0x7,%edx
    1266:	lea    (%rax,%rsi,4),%r8
    126a:	add    $0xfffffffffffffff0,%r8
    126e:	lea    (%rcx,%rsi,4),%r9
    1272:	add    $0xfffffffffffffff0,%r9
    1276:	mov    %rdi,%r10
    1279:	neg    %r10
    127c:	xor    %r11d,%r11d
    127f:	nop
    1280:	movdqu -0x10(%r8,%r11,4),%xmm0
    1287:	movdqu (%r8,%r11,4),%xmm1
    128d:	paddd  %xmm1,%xmm1
    1291:	paddd  %xmm0,%xmm0
    1295:	movdqu %xmm1,(%r9,%r11,4)
    129b:	movdqu %xmm0,-0x10(%r9,%r11,4)
    12a2:	add    $0xfffffffffffffff8,%r11
    12a6:	cmp    %r11,%r10
    12a9:	jne    1280 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    12ab:	cmp    %rdi,%rsi
    12ae:	je     1314 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12b0:	lea    -0x1(%rdx),%rdi
    12b4:	mov    %rdx,%r8
    12b7:	and    $0x3,%r8
    12bb:	je     1315 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf5>
    12bd:	nopl   (%rax)
    12c0:	lea    -0x1(%rdx),%rsi
    12c4:	mov    -0x4(%rax,%rdx,4),%r9d
    12c9:	add    %r9d,%r9d
    12cc:	mov    %r9d,-0x4(%rcx,%rdx,4)
    12d1:	mov    %rsi,%rdx
    12d4:	dec    %r8
    12d7:	jne    12c0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12d9:	cmp    $0x3,%rdi
    12dd:	jb     1314 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12df:	nop
    12e0:	mov    -0x4(%rax,%rsi,4),%edx
    12e4:	add    %edx,%edx
    12e6:	mov    %edx,-0x4(%rcx,%rsi,4)
    12ea:	mov    -0x8(%rax,%rsi,4),%edx
    12ee:	add    %edx,%edx
    12f0:	mov    %edx,-0x8(%rcx,%rsi,4)
    12f4:	mov    -0xc(%rax,%rsi,4),%edx
    12f8:	add    %edx,%edx
    12fa:	mov    %edx,-0xc(%rcx,%rsi,4)
    12fe:	mov    -0x10(%rax,%rsi,4),%edx
    1302:	add    %edx,%edx
    1304:	mov    %edx,-0x10(%rcx,%rsi,4)
    1308:	lea    -0x4(%rsi),%rdx
    130c:	mov    %rdx,%rsi
    130f:	test   %rdx,%rdx
    1312:	jne    12e0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1314:	ret
    1315:	mov    %rdx,%rsi
    1318:	cmp    $0x3,%rdi
    131c:	jae    12e0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    131e:	jmp    1314 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
