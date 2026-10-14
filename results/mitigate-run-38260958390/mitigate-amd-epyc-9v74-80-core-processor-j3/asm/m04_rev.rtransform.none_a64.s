0000000000001280 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rsi),%rax
    1283:	mov    0x8(%rsi),%rsi
    1287:	mov    %rsi,%r8
    128a:	sub    %rax,%r8
    128d:	je     1354 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd4>
    1293:	mov    0x8(%rdi),%rdi
    1297:	add    $0xfffffffffffffffc,%r8
    129b:	cmp    $0x1c,%r8
    129f:	jb     1334 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb4>
    12a5:	mov    %rsi,%rcx
    12a8:	sub    %rdi,%rcx
    12ab:	cmp    $0x20,%rcx
    12af:	jb     1334 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb4>
    12b5:	shr    $0x2,%r8
    12b9:	inc    %r8
    12bc:	mov    %r8,%r9
    12bf:	and    $0xfffffffffffffff8,%r9
    12c3:	lea    0x0(,%r9,4),%r10
    12cb:	mov    %rsi,%rcx
    12ce:	sub    %r10,%rcx
    12d1:	mov    %rdi,%rdx
    12d4:	sub    %r10,%rdx
    12d7:	mov    %r9,%r10
    12da:	neg    %r10
    12dd:	xor    %r11d,%r11d
    12e0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ef:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fe:	xchg   %ax,%ax
    1300:	movdqu -0x20(%rsi,%r11,4),%xmm0
    1307:	movdqu -0x10(%rsi,%r11,4),%xmm1
    130e:	paddd  %xmm1,%xmm1
    1312:	paddd  %xmm0,%xmm0
    1316:	movdqu %xmm1,-0x10(%rdi,%r11,4)
    131d:	movdqu %xmm0,-0x20(%rdi,%r11,4)
    1324:	add    $0xfffffffffffffff8,%r11
    1328:	cmp    %r11,%r10
    132b:	jne    1300 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    132d:	cmp    %r9,%r8
    1330:	jne    133a <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xba>
    1332:	jmp    1354 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd4>
    1334:	mov    %rsi,%rcx
    1337:	mov    %rdi,%rdx
    133a:	add    $0xfffffffffffffffc,%rdx
    133e:	xchg   %ax,%ax
    1340:	mov    -0x4(%rcx),%esi
    1343:	add    $0xfffffffffffffffc,%rcx
    1347:	add    %esi,%esi
    1349:	mov    %esi,(%rdx)
    134b:	add    $0xfffffffffffffffc,%rdx
    134f:	cmp    %rax,%rcx
    1352:	jne    1340 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1354:	ret
    1355:	data16 cs nopw 0x0(%rax,%rax,1)
