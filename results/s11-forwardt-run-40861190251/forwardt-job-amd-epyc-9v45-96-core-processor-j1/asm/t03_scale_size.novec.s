0000000000001220 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rcx
    1223:	mov    0x8(%rsi),%r8
    1227:	sub    %rcx,%r8
    122a:	je     12c0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    1230:	sar    $0x2,%r8
    1234:	cmp    $0x1,%r8
    1238:	mov    %r8,%rsi
    123b:	adc    $0x0,%rsi
    123f:	mov    (%rdi),%rdx
    1242:	mov    %esi,%eax
    1244:	and    $0x3,%eax
    1247:	cmp    $0x4,%r8
    124b:	jae    1251 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x31>
    124d:	xor    %edi,%edi
    124f:	jmp    129b <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7b>
    1251:	and    $0xfffffffffffffffc,%rsi
    1255:	xor    %edi,%edi
    1257:	nopw   0x0(%rax,%rax,1)
    1260:	mov    (%rcx,%rdi,4),%r8d
    1264:	add    %r8d,%r8d
    1267:	mov    %r8d,(%rdx,%rdi,4)
    126b:	mov    0x4(%rcx,%rdi,4),%r8d
    1270:	add    %r8d,%r8d
    1273:	mov    %r8d,0x4(%rdx,%rdi,4)
    1278:	mov    0x8(%rcx,%rdi,4),%r8d
    127d:	add    %r8d,%r8d
    1280:	mov    %r8d,0x8(%rdx,%rdi,4)
    1285:	mov    0xc(%rcx,%rdi,4),%r8d
    128a:	add    %r8d,%r8d
    128d:	mov    %r8d,0xc(%rdx,%rdi,4)
    1292:	add    $0x4,%rdi
    1296:	cmp    %rdi,%rsi
    1299:	jne    1260 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    129b:	test   %rax,%rax
    129e:	je     12c0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12a0:	lea    (%rdx,%rdi,4),%rdx
    12a4:	lea    (%rcx,%rdi,4),%rcx
    12a8:	xor    %esi,%esi
    12aa:	nopw   0x0(%rax,%rax,1)
    12b0:	mov    (%rcx,%rsi,4),%edi
    12b3:	add    %edi,%edi
    12b5:	mov    %edi,(%rdx,%rsi,4)
    12b8:	inc    %rsi
    12bb:	cmp    %rsi,%rax
    12be:	jne    12b0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>
    12c0:	ret
    12c1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
