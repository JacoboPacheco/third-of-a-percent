0000000000001240 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rsi
    1247:	sub    %rax,%rsi
    124a:	je     1334 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    1250:	sar    $0x2,%rsi
    1254:	mov    (%rdi),%rcx
    1257:	cmp    $0x8,%rsi
    125b:	jb     12c2 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x82>
    125d:	mov    %rax,%rdx
    1260:	sub    %rcx,%rdx
    1263:	cmp    $0x20,%rdx
    1267:	jb     12c2 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x82>
    1269:	mov    %rsi,%rdi
    126c:	and    $0xfffffffffffffff8,%rdi
    1270:	mov    %esi,%edx
    1272:	and    $0x7,%edx
    1275:	lea    (%rax,%rsi,4),%r8
    1279:	add    $0xfffffffffffffff0,%r8
    127d:	lea    (%rcx,%rsi,4),%r9
    1281:	add    $0xfffffffffffffff0,%r9
    1285:	mov    %rdi,%r10
    1288:	neg    %r10
    128b:	xor    %r11d,%r11d
    128e:	xchg   %ax,%ax
    1290:	movdqu -0x10(%r8,%r11,4),%xmm0
    1297:	movdqu (%r8,%r11,4),%xmm1
    129d:	paddd  %xmm1,%xmm1
    12a1:	paddd  %xmm0,%xmm0
    12a5:	movdqu %xmm1,(%r9,%r11,4)
    12ab:	movdqu %xmm0,-0x10(%r9,%r11,4)
    12b2:	add    $0xfffffffffffffff8,%r11
    12b6:	cmp    %r11,%r10
    12b9:	jne    1290 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x50>
    12bb:	cmp    %rdi,%rsi
    12be:	jne    12c5 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    12c0:	jmp    1334 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12c2:	mov    %rsi,%rdx
    12c5:	lea    -0x1(%rdx),%rdi
    12c9:	mov    %rdx,%r8
    12cc:	and    $0x3,%r8
    12d0:	je     1335 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf5>
    12d2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e0:	lea    -0x1(%rdx),%rsi
    12e4:	mov    -0x4(%rax,%rdx,4),%r9d
    12e9:	add    %r9d,%r9d
    12ec:	mov    %r9d,-0x4(%rcx,%rdx,4)
    12f1:	mov    %rsi,%rdx
    12f4:	dec    %r8
    12f7:	jne    12e0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12f9:	cmp    $0x3,%rdi
    12fd:	jb     1334 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12ff:	nop
    1300:	mov    -0x4(%rax,%rsi,4),%edx
    1304:	add    %edx,%edx
    1306:	mov    %edx,-0x4(%rcx,%rsi,4)
    130a:	mov    -0x8(%rax,%rsi,4),%edx
    130e:	add    %edx,%edx
    1310:	mov    %edx,-0x8(%rcx,%rsi,4)
    1314:	mov    -0xc(%rax,%rsi,4),%edx
    1318:	add    %edx,%edx
    131a:	mov    %edx,-0xc(%rcx,%rsi,4)
    131e:	mov    -0x10(%rax,%rsi,4),%edx
    1322:	add    %edx,%edx
    1324:	mov    %edx,-0x10(%rcx,%rsi,4)
    1328:	lea    -0x4(%rsi),%rdx
    132c:	mov    %rdx,%rsi
    132f:	test   %rdx,%rdx
    1332:	jne    1300 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1334:	ret
    1335:	mov    %rdx,%rsi
    1338:	cmp    $0x3,%rdi
    133c:	jae    1300 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    133e:	jmp    1334 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
