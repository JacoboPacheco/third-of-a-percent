0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdx),%rdx
    1257:	mov    (%rdi),%rsi
    125a:	cmp    $0x1,%rcx
    125e:	mov    %rcx,%rdi
    1261:	adc    $0x0,%rdi
    1265:	cmp    $0xc,%rcx
    1269:	jae    1344 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x104>
    126f:	xor    %r8d,%r8d
    1272:	mov    %rdi,%r10
    1275:	mov    %r8,%r9
    1278:	and    $0x3,%r10
    127c:	je     12d4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x94>
    127e:	mov    %r8,%r9
    1281:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1290:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    129f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ae:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bd:	nopl   (%rax)
    12c0:	mov    (%rdx,%r9,4),%r11d
    12c4:	add    (%rax,%r9,4),%r11d
    12c8:	mov    %r11d,(%rsi,%r9,4)
    12cc:	inc    %r9
    12cf:	dec    %r10
    12d2:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12d4:	sub    %rdi,%r8
    12d7:	cmp    $0xfffffffffffffffc,%r8
    12db:	ja     13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	mov    (%rdx,%r9,4),%edi
    1304:	add    (%rax,%r9,4),%edi
    1308:	mov    %edi,(%rsi,%r9,4)
    130c:	mov    0x4(%rdx,%r9,4),%edi
    1311:	add    0x4(%rax,%r9,4),%edi
    1316:	mov    %edi,0x4(%rsi,%r9,4)
    131b:	mov    0x8(%rdx,%r9,4),%edi
    1320:	add    0x8(%rax,%r9,4),%edi
    1325:	mov    %edi,0x8(%rsi,%r9,4)
    132a:	mov    0xc(%rdx,%r9,4),%edi
    132f:	add    0xc(%rax,%r9,4),%edi
    1334:	mov    %edi,0xc(%rsi,%r9,4)
    1339:	add    $0x4,%r9
    133d:	cmp    %r9,%rcx
    1340:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1342:	jmp    13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    1344:	mov    %rsi,%r9
    1347:	sub    %rax,%r9
    134a:	xor    %r8d,%r8d
    134d:	cmp    $0x20,%r9
    1351:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1357:	mov    %rsi,%r9
    135a:	sub    %rdx,%r9
    135d:	cmp    $0x20,%r9
    1361:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1367:	mov    %rdi,%r8
    136a:	and    $0xfffffffffffffff8,%r8
    136e:	xor    %r9d,%r9d
    1371:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	movdqu (%rax,%r9,4),%xmm0
    1386:	movdqu 0x10(%rax,%r9,4),%xmm1
    138d:	movdqu (%rdx,%r9,4),%xmm2
    1393:	paddd  %xmm0,%xmm2
    1397:	movdqu 0x10(%rdx,%r9,4),%xmm0
    139e:	paddd  %xmm1,%xmm0
    13a2:	movdqu %xmm2,(%rsi,%r9,4)
    13a8:	movdqu %xmm0,0x10(%rsi,%r9,4)
    13af:	add    $0x8,%r9
    13b3:	cmp    %r9,%r8
    13b6:	jne    1380 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x140>
    13b8:	cmp    %r8,%rdi
    13bb:	jne    1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    13c1:	ret
    13c2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
