0000000000001240 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rdx
    1247:	sub    %rax,%rdx
    124a:	je     1267 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x27>
    124c:	sar    $0x2,%rdx
    1250:	cmp    $0x1,%rdx
    1254:	mov    %rdx,%rcx
    1257:	adc    $0x0,%rcx
    125b:	cmp    $0x4,%rdx
    125f:	jae    126b <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x2b>
    1261:	xor    %edx,%edx
    1263:	xor    %edi,%edi
    1265:	jmp    12d1 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x91>
    1267:	xor    %edi,%edi
    1269:	jmp    12c8 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x88>
    126b:	mov    %rcx,%rdx
    126e:	and    $0xfffffffffffffffc,%rdx
    1272:	pxor   %xmm0,%xmm0
    1276:	xor    %edi,%edi
    1278:	pxor   %xmm1,%xmm1
    127c:	nopl   0x0(%rax)
    1280:	movq   (%rax,%rdi,4),%xmm2
    1285:	movq   0x8(%rax,%rdi,4),%xmm3
    128b:	pxor   %xmm4,%xmm4
    128f:	pcmpgtd %xmm2,%xmm4
    1293:	punpckldq %xmm4,%xmm2
    1297:	paddq  %xmm2,%xmm0
    129b:	pxor   %xmm2,%xmm2
    129f:	pcmpgtd %xmm3,%xmm2
    12a3:	punpckldq %xmm2,%xmm3
    12a7:	paddq  %xmm3,%xmm1
    12ab:	add    $0x4,%rdi
    12af:	cmp    %rdi,%rdx
    12b2:	jne    1280 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x40>
    12b4:	paddq  %xmm0,%xmm1
    12b8:	pshufd $0xee,%xmm1,%xmm0
    12bd:	paddq  %xmm1,%xmm0
    12c1:	movq   %xmm0,%rdi
    12c6:	jmp    12cc <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x8c>
    12c8:	mov    %rdi,(%rsi)
    12cb:	ret
    12cc:	cmp    %rdx,%rcx
    12cf:	je     12c8 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x88>
    12d1:	movslq (%rax,%rdx,4),%r8
    12d5:	add    %r8,%rdi
    12d8:	inc    %rdx
    12db:	jmp    12cc <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x8c>
    12dd:	nopl   (%rax)
