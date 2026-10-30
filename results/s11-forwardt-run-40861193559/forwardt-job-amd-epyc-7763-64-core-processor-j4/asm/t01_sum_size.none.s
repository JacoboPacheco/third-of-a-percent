0000000000001220 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%rdx
    1227:	sub    %rax,%rdx
    122a:	je     1247 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x27>
    122c:	sar    $0x2,%rdx
    1230:	cmp    $0x1,%rdx
    1234:	mov    %rdx,%rcx
    1237:	adc    $0x0,%rcx
    123b:	cmp    $0x4,%rdx
    123f:	jae    124b <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x2b>
    1241:	xor    %edx,%edx
    1243:	xor    %edi,%edi
    1245:	jmp    12b1 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x91>
    1247:	xor    %edi,%edi
    1249:	jmp    12a8 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x88>
    124b:	mov    %rcx,%rdx
    124e:	and    $0xfffffffffffffffc,%rdx
    1252:	pxor   %xmm0,%xmm0
    1256:	xor    %edi,%edi
    1258:	pxor   %xmm1,%xmm1
    125c:	nopl   0x0(%rax)
    1260:	movq   (%rax,%rdi,4),%xmm2
    1265:	movq   0x8(%rax,%rdi,4),%xmm3
    126b:	pxor   %xmm4,%xmm4
    126f:	pcmpgtd %xmm2,%xmm4
    1273:	punpckldq %xmm4,%xmm2
    1277:	paddq  %xmm2,%xmm0
    127b:	pxor   %xmm2,%xmm2
    127f:	pcmpgtd %xmm3,%xmm2
    1283:	punpckldq %xmm2,%xmm3
    1287:	paddq  %xmm3,%xmm1
    128b:	add    $0x4,%rdi
    128f:	cmp    %rdi,%rdx
    1292:	jne    1260 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x40>
    1294:	paddq  %xmm0,%xmm1
    1298:	pshufd $0xee,%xmm1,%xmm0
    129d:	paddq  %xmm1,%xmm0
    12a1:	movq   %xmm0,%rdi
    12a6:	jmp    12ac <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x8c>
    12a8:	mov    %rdi,(%rsi)
    12ab:	ret
    12ac:	cmp    %rdx,%rcx
    12af:	je     12a8 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x88>
    12b1:	movslq (%rax,%rdx,4),%r8
    12b5:	add    %r8,%rdi
    12b8:	inc    %rdx
    12bb:	jmp    12ac <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x8c>
    12bd:	nopl   (%rax)
