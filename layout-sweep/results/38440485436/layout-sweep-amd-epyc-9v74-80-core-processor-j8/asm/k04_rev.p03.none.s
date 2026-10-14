0000000000001250 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1250:	mov    (%rsi),%rax
    1253:	mov    0x8(%rsi),%rsi
    1257:	sub    %rax,%rsi
    125a:	je     1344 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    1260:	sar    $0x2,%rsi
    1264:	mov    (%rdi),%rcx
    1267:	cmp    $0x8,%rsi
    126b:	jb     12d2 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x82>
    126d:	mov    %rax,%rdx
    1270:	sub    %rcx,%rdx
    1273:	cmp    $0x20,%rdx
    1277:	jb     12d2 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x82>
    1279:	mov    %rsi,%rdi
    127c:	and    $0xfffffffffffffff8,%rdi
    1280:	mov    %esi,%edx
    1282:	and    $0x7,%edx
    1285:	lea    (%rax,%rsi,4),%r8
    1289:	add    $0xfffffffffffffff0,%r8
    128d:	lea    (%rcx,%rsi,4),%r9
    1291:	add    $0xfffffffffffffff0,%r9
    1295:	mov    %rdi,%r10
    1298:	neg    %r10
    129b:	xor    %r11d,%r11d
    129e:	xchg   %ax,%ax
    12a0:	movdqu -0x10(%r8,%r11,4),%xmm0
    12a7:	movdqu (%r8,%r11,4),%xmm1
    12ad:	paddd  %xmm1,%xmm1
    12b1:	paddd  %xmm0,%xmm0
    12b5:	movdqu %xmm1,(%r9,%r11,4)
    12bb:	movdqu %xmm0,-0x10(%r9,%r11,4)
    12c2:	add    $0xfffffffffffffff8,%r11
    12c6:	cmp    %r11,%r10
    12c9:	jne    12a0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x50>
    12cb:	cmp    %rdi,%rsi
    12ce:	jne    12d5 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    12d0:	jmp    1344 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12d2:	mov    %rsi,%rdx
    12d5:	lea    -0x1(%rdx),%rdi
    12d9:	mov    %rdx,%r8
    12dc:	and    $0x3,%r8
    12e0:	je     1345 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf5>
    12e2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	lea    -0x1(%rdx),%rsi
    12f4:	mov    -0x4(%rax,%rdx,4),%r9d
    12f9:	add    %r9d,%r9d
    12fc:	mov    %r9d,-0x4(%rcx,%rdx,4)
    1301:	mov    %rsi,%rdx
    1304:	dec    %r8
    1307:	jne    12f0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    1309:	cmp    $0x3,%rdi
    130d:	jb     1344 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    130f:	nop
    1310:	mov    -0x4(%rax,%rsi,4),%edx
    1314:	add    %edx,%edx
    1316:	mov    %edx,-0x4(%rcx,%rsi,4)
    131a:	mov    -0x8(%rax,%rsi,4),%edx
    131e:	add    %edx,%edx
    1320:	mov    %edx,-0x8(%rcx,%rsi,4)
    1324:	mov    -0xc(%rax,%rsi,4),%edx
    1328:	add    %edx,%edx
    132a:	mov    %edx,-0xc(%rcx,%rsi,4)
    132e:	mov    -0x10(%rax,%rsi,4),%edx
    1332:	add    %edx,%edx
    1334:	mov    %edx,-0x10(%rcx,%rsi,4)
    1338:	lea    -0x4(%rsi),%rdx
    133c:	mov    %rdx,%rsi
    133f:	test   %rdx,%rdx
    1342:	jne    1310 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1344:	ret
    1345:	mov    %rdx,%rsi
    1348:	cmp    $0x3,%rdi
    134c:	jae    1310 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    134e:	jmp    1344 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
