0000000000001240 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1240:	mov    (%rdi),%rcx
    1243:	mov    0x8(%rdi),%rax
    1247:	sub    %rcx,%rax
    124a:	je     1267 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x27>
    124c:	sar    $0x2,%rax
    1250:	cmp    $0x1,%rax
    1254:	mov    %rax,%rdx
    1257:	adc    $0x0,%rdx
    125b:	cmp    $0x4,%rax
    125f:	jae    126b <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2b>
    1261:	xor    %esi,%esi
    1263:	xor    %eax,%eax
    1265:	jmp    12ce <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x8e>
    1267:	xor    %eax,%eax
    1269:	jmp    12c8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    126b:	mov    %rdx,%rsi
    126e:	and    $0xfffffffffffffffc,%rsi
    1272:	pxor   %xmm0,%xmm0
    1276:	xor    %eax,%eax
    1278:	pxor   %xmm1,%xmm1
    127c:	nopl   0x0(%rax)
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
    12c6:	jmp    12c9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12c8:	ret
    12c9:	cmp    %rsi,%rdx
    12cc:	je     12c8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    12ce:	movslq (%rcx,%rsi,4),%rdi
    12d2:	add    %rdi,%rax
    12d5:	inc    %rsi
    12d8:	jmp    12c9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12da:	nopw   0x0(%rax,%rax,1)
