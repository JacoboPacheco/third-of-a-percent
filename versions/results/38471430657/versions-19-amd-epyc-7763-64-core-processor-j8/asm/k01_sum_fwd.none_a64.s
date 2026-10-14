0000000000001240 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1240:	mov    (%rdi),%rcx
    1243:	mov    0x8(%rdi),%rdi
    1247:	sub    %rcx,%rdi
    124a:	je     126a <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2a>
    124c:	sar    $0x2,%rdi
    1250:	cmp    $0x1,%rdi
    1254:	mov    %rdi,%rdx
    1257:	adc    $0x0,%rdx
    125b:	cmp    $0x3,%rdi
    125f:	ja     126d <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2d>
    1261:	xor    %esi,%esi
    1263:	xor    %eax,%eax
    1265:	jmp    1300 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xc0>
    126a:	xor    %eax,%eax
    126c:	ret
    126d:	mov    %rdx,%rsi
    1270:	and    $0xfffffffffffffffc,%rsi
    1274:	pxor   %xmm0,%xmm0
    1278:	xor    %eax,%eax
    127a:	pxor   %xmm1,%xmm1
    127e:	xchg   %ax,%ax
    1280:	movq   (%rcx,%rax,4),%xmm2
    1285:	movq   0x8(%rcx,%rax,4),%xmm3
    128b:	pxor   %xmm4,%xmm4
    128f:	pcmpgtd %xmm2,%xmm4
    1293:	punpckldq %xmm4,%xmm2
    1297:	paddq  %xmm2,%xmm0
    129b:	pxor   %xmm2,%xmm2
    129f:	pcmpgtd %xmm3,%xmm2
    12a3:	punpckldq %xmm2,%xmm3
    12a7:	paddq  %xmm3,%xmm1
    12ab:	add    $0x4,%rax
    12af:	cmp    %rax,%rsi
    12b2:	jne    1280 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x40>
    12b4:	paddq  %xmm0,%xmm1
    12b8:	pshufd $0xee,%xmm1,%xmm0
    12bd:	paddq  %xmm1,%xmm0
    12c1:	movq   %xmm0,%rax
    12c6:	cmp    %rsi,%rdi
    12c9:	je     130f <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xcf>
    12cb:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12da:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f8:	nopl   0x0(%rax,%rax,1)
    1300:	movslq (%rcx,%rsi,4),%rdi
    1304:	add    %rdi,%rax
    1307:	inc    %rsi
    130a:	cmp    %rsi,%rdx
    130d:	jne    1300 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xc0>
    130f:	ret
